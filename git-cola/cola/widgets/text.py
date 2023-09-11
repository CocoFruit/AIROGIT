"""Text widgets"""
# pylint: disable=unexpected-keyword-arg
from functools import partial
import math

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from qtpy.QtCore import Qt
from qtpy.QtCore import Signal

from ..models import prefs
from ..qtutils import get
from .. import hotkeys
from .. import icons
from .. import qtutils
from .. import utils
from ..i18n import N_
from . import defs


def get_stripped(widget):
    return widget.get().strip()


class LineEdit(QtWidgets.QLineEdit):
    cursor_changed = Signal(int, int)
    esc_pressed = Signal()

    def __init__(self, parent=None, row=1, get_value=None, clear_button=False):
        QtWidgets.QLineEdit.__init__(self, parent)
        self._row = row
        if get_value is None:
            get_value = get_stripped
        self._get_value = get_value
        self.cursor_position = LineEditCursorPosition(self, row)
        self.menu_actions = []

        if clear_button and hasattr(self, 'setClearButtonEnabled'):
            self.setClearButtonEnabled(True)

    def get(self):
        """Return the raw unicode value from Qt"""
        return self.text()

    def value(self):
        """Return the processed value, e.g. stripped"""
        return self._get_value(self)

    def set_value(self, value, block=False):
        """Update the widget to the specified value"""
        if block:
            with qtutils.BlockSignals(self):
                self._set_value(value)
        else:
            self._set_value(value)

    def _set_value(self, value):
        """Implementation helper to update the widget to the specified value"""
        pos = self.cursorPosition()
        self.setText(value)
        self.setCursorPosition(pos)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self.esc_pressed.emit()
        super().keyPressEvent(event)


class LineEditCursorPosition:
    """Translate cursorPositionChanged(int,int) into cursorPosition(int,int)"""

    def __init__(self, widget, row):
        self._widget = widget
        self._row = row
        # Translate cursorPositionChanged into cursor_changed(int, int)
        widget.cursorPositionChanged.connect(lambda old, new: self.emit())

    def emit(self):
        widget = self._widget
        row = self._row
        col = widget.cursorPosition()
        widget.cursor_changed.emit(row, col)

    def reset(self):
        self._widget.setCursorPosition(0)


class BaseTextEditExtension(QtCore.QObject):
    def __init__(self, widget, get_value, readonly):
        QtCore.QObject.__init__(self, widget)
        self.widget = widget
        self.cursor_position = TextEditCursorPosition(widget, self)
        if get_value is None:
            get_value = get_stripped
        self._get_value = get_value
        self._tabwidth = 8
        self._readonly = readonly
        self._init_flags()
        self.init()

    def _init_flags(self):
        widget = self.widget
        widget.setMinimumSize(QtCore.QSize(10, 10))
        widget.setWordWrapMode(QtGui.QTextOption.WordWrap)
        widget.setLineWrapMode(widget.NoWrap)
        if self._readonly:
            widget.setReadOnly(True)
            widget.setAcceptDrops(False)
            widget.setTabChangesFocus(True)
            widget.setUndoRedoEnabled(False)
            widget.setTextInteractionFlags(
                Qt.TextSelectableByKeyboard | Qt.TextSelectableByMouse
            )

    def get(self):
        """Return the raw unicode value from Qt"""
        return self.widget.toPlainText()

    def value(self):
        """Return a safe value, e.g. a stripped value"""
        return self._get_value(self.widget)

    def set_value(self, value, block=False):
        """Update the widget to the specified value"""
        if block:
            with qtutils.BlockSignals(self):
                self._set_value(value)
        else:
            self._set_value(value)

    def _set_value(self, value):
        """Implementation helper to update the widget to the specified value"""
        # Save cursor position
        offset, selection_text = self.offset_and_selection()
        old_value = get(self.widget)

        # Update text
        self.widget.setPlainText(value)

        # Restore cursor
        if selection_text and selection_text in value:
            # If the old selection exists in the new text then re-select it.
            idx = value.index(selection_text)
            cursor = self.widget.textCursor()
            cursor.setPosition(idx)
            cursor.setPosition(idx + len(selection_text), QtGui.QTextCursor.KeepAnchor)
            self.widget.setTextCursor(cursor)

        elif value == old_value:
            # Otherwise, if the text is identical and there is no selection
            # then restore the cursor position.
            cursor = self.widget.textCursor()
            cursor.setPosition(offset)
            self.widget.setTextCursor(cursor)
        else:
            # If none of the above applied then restore the cursor position.
            position = max(0, min(offset, len(value) - 1))
            cursor = self.widget.textCursor()
            cursor.setPosition(position)
            self.widget.setTextCursor(cursor)
            cursor = self.widget.textCursor()
            cursor.movePosition(QtGui.QTextCursor.StartOfLine)
            self.widget.setTextCursor(cursor)

    def set_cursor_position(self, new_position):
        cursor = self.widget.textCursor()
        cursor.setPosition(new_position)
        self.widget.setTextCursor(cursor)

    def tabwidth(self):
        return self._tabwidth

    def set_tabwidth(self, width):
        self._tabwidth = width
        font = self.widget.font()
        metrics = QtGui.QFontMetrics(font)
        pixels = metrics.width('M' * width)
        self.widget.setTabStopWidth(pixels)

    def selected_line(self):
        contents = self.value()
        cursor = self.widget.textCursor()
        offset = min(cursor.position(), len(contents) - 1)
        while offset >= 1 and contents[offset - 1] and contents[offset - 1] != '\n':
            offset -= 1
        data = contents[offset:]
        if '\n' in data:
            line, _ = data.split('\n', 1)
        else:
            line = data
        return line

    def cursor(self):
        return self.widget.textCursor()

    def has_selection(self):
        return self.cursor().hasSelection()

    def selected_text(self):
        """Return the selected text"""
        _, selection = self.offset_and_selection()
        return selection

    def offset_and_selection(self):
        """Return the cursor offset and selected text"""
        cursor = self.cursor()
        offset = cursor.selectionStart()
        selection_text = cursor.selection().toPlainText()
        return offset, selection_text

    def mouse_press_event(self, event):
        # Move the text cursor so that the right-click events operate
        # on the current position, not the last left-clicked position.
        widget = self.widget
        if event.button() == Qt.RightButton:
            if not widget.textCursor().hasSelection():
                cursor = widget.cursorForPosition(event.pos())
                widget.setTextCursor(cursor)

    def add_links_to_menu(self, menu):
        """Add actions for opening URLs to a custom menu"""
        links = self._get_links()
        if links:
            menu.addSeparator()
        for url in links:
            action = menu.addAction(N_('Open "%s"') % url)
            action.setIcon(icons.external())
            qtutils.connect_action(
                action, partial(QtGui.QDesktopServices.openUrl, QtCore.QUrl(url))
            )

    def _get_links(self):
        """Return http links on the current line"""
        _, selection = self.offset_and_selection()
        if selection:
            line = selection
        else:
            line = self.selected_line()
        if not line:
            return []
        return [
            word for word in line.split() if word.startswith(('http://', 'https://'))
        ]

    def create_context_menu(self, event_pos):
        """Create a context menu for a widget"""
        menu = self.widget.createStandardContextMenu(event_pos)
        qtutils.add_menu_actions(menu, self.widget.menu_actions)
        self.add_links_to_menu(menu)
        return menu

    def context_menu_event(self, event):
        """Default context menu event"""
        event_pos = event.pos()
        menu = self.widget.create_context_menu(event_pos)
        menu.exec_(self.widget.mapToGlobal(event_pos))

    # For extension by sub-classes

    def init(self):
        """Called during init for class-specific settings"""
        return

    # pylint: disable=unused-argument
    def set_textwidth(self, width):
        """Set the text width"""
        return

    # pylint: disable=unused-argument
    def set_linebreak(self, brk):
        """Enable word wrapping"""
        return


class PlainTextEditExtension(BaseTextEditExtension):
    def set_linebreak(self, brk):
        if brk:
            wrapmode = QtWidgets.QPlainTextEdit.WidgetWidth
        else:
            wrapmode = QtWidgets.QPlainTextEdit.NoWrap
        self.widget.setLineWrapMode(wrapmode)


class PlainTextEdit(QtWidgets.QPlainTextEdit):
    cursor_changed = Signal(int, int)
    leave = Signal()

    def __init__(self, parent=None, get_value=None, readonly=False, options=None):
        QtWidgets.QPlainTextEdit.__init__(self, parent)
        self.ext = PlainTextEditExtension(self, get_value, readonly)
        self.cursor_position = self.ext.cursor_position
        self.mouse_zoom = True
        self.options = options
        self.menu_actions = []

    def get(self):
        """Return the raw unicode value from Qt"""
        return self.ext.get()

    # For compatibility with QTextEdit
    def setText(self, value):
        self.set_value(value)

    def value(self):
        """Return a safe value, e.g. a stripped value"""
        return self.ext.value()

    def offset_and_selection(self):
        """Return the cursor offset and selected text"""
        return self.ext.offset_and_selection()

    def set_value(self, value, block=False):
        self.ext.set_value(value, block=block)

    def set_mouse_zoom(self, value):
        """Enable/disable text zooming in response to ctrl + mousewheel scroll events"""
        self.mouse_zoom = value

    def set_options(self, options):
        """Register an Options widget"""
        self.options = options

    def set_word_wrapping(self, enabled, update=False):
        """Enable/disable word wrapping"""
        if update and self.options is not None:
            with qtutils.BlockSignals(self.options.enable_word_wrapping):
                self.options.enable_word_wrapping.setChecked(enabled)
        if enabled:
            self.setWordWrapMode(QtGui.QTextOption.WordWrap)
            self.setLineWrapMode(QtWidgets.QPlainTextEdit.WidgetWidth)
        else:
            self.setWordWrapMode(QtGui.QTextOption.NoWrap)
            self.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)

    def has_selection(self):
        return self.ext.has_selection()

    def selected_line(self):
        return self.ext.selected_line()

    def selected_text(self):
        """Return the selected text"""
        return self.ext.selected_text()

    def set_tabwidth(self, width):
        self.ext.set_tabwidth(width)

    def set_textwidth(self, width):
        self.ext.set_textwidth(width)

    def set_linebreak(self, brk):
        self.ext.set_linebreak(brk)

    def mousePressEvent(self, event):
        self.ext.mouse_press_event(event)
        super().mousePressEvent(event)

    def wheelEvent(self, event):
        """Disable control+wheelscroll text resizing"""
        if not self.mouse_zoom and (event.modifiers() & Qt.ControlModifier):
            event.ignore()
            return
        super().wheelEvent(event)

    def create_context_menu(self, event_pos):
        """Create a custom context menu"""
        return self.ext.create_context_menu(event_pos)

    def contextMenuEvent(self, event):
        """Custom contextMenuEvent() for building our custom context menus"""
        self.ext.context_menu_event(event)


class TextSearchWidget(QtWidgets.QWidget):
    """The search dialog that displays over a text edit field"""

    def __init__(self, widget, parent):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self._widget = widget
        self._parent = parent

        self.text = HintedDefaultLineEdit(N_('Find in diff'), parent=self)

        self.prev_button = qtutils.create_action_button(
            tooltip=N_('Find the previous occurrence of the phrase'), icon=icons.up()
        )

        self.next_button = qtutils.create_action_button(
            tooltip=N_('Find the next occurrence of the phrase'), icon=icons.down()
        )

        self.match_case_checkbox = qtutils.checkbox(N_('Match Case'))
        self.whole_words_checkbox = qtutils.checkbox(N_('Whole Words'))

        self.close_button = qtutils.create_action_button(
            tooltip=N_('Close the find bar'), icon=icons.close()
        )

        layout = qtutils.hbox(
            defs.margin,
            defs.button_spacing,
            self.text,
            self.prev_button,
            self.next_button,
            self.match_case_checkbox,
            self.whole_words_checkbox,
            qtutils.STRETCH,
            self.close_button,
        )
        self.setLayout(layout)
        self.setFocusProxy(self.text)

        self.text.esc_pressed.connect(self.hide_search)
        self.text.returnPressed.connect(self.search)
        self.text.textChanged.connect(self.search)

        self.search_next_action = qtutils.add_action(
            parent,
            N_('Find next item'),
            self.search,
            hotkeys.SEARCH_NEXT,
        )
        self.search_prev_action = qtutils.add_action(
            parent,
            N_('Find previous item'),
            self.search_backwards,
            hotkeys.SEARCH_PREV,
        )

        qtutils.connect_button(self.next_button, self.search)
        qtutils.connect_button(self.prev_button, self.search_backwards)
        qtutils.connect_button(self.close_button, self.hide_search)
        qtutils.connect_checkbox(self.match_case_checkbox, lambda _: self.search())
        qtutils.connect_checkbox(self.whole_words_checkbox, lambda _: self.search())

    def search(self):
        """Emit a signal with the current search text"""
        self.search_text(backwards=False)

    def search_backwards(self):
        """Emit a signal with the current search text for a backwards search"""
        self.search_text(backwards=True)

    def hide_search(self):
        """Hide the search window"""
        self.hide()
        self._parent.setFocus(True)

    def find_flags(self, backwards):
        """Return QTextDocument.FindFlags for the current search options"""
        flags = QtGui.QTextDocument.FindFlags()
        if backwards:
            flags = flags | QtGui.QTextDocument.FindBackward
        if self.match_case_checkbox.isChecked():
            flags = flags | QtGui.QTextDocument.FindCaseSensitively
        if self.whole_words_checkbox.isChecked():
            flags = flags | QtGui.QTextDocument.FindWholeWords
        return flags

    def is_case_sensitive(self):
        """Are we searching using a case-insensitive search?"""
        return self.match_case_checkbox.isChecked()

    def search_text(self, backwards=False):
        """Search the diff text for the given text"""
        text = self.text.get()
        cursor = self._widget.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            case_sensitive = self.is_case_sensitive()
            if text_matches(case_sensitive, selected_text, text):
                if backwards:
                    position = cursor.selectionStart()
                else:
                    position = cursor.selectionEnd()
            else:
                if backwards:
                    position = cursor.selectionEnd()
                else:
                    position = cursor.selectionStart()
            cursor.setPosition(position)
            self._widget.setTextCursor(cursor)

        flags = self.find_flags(backwards)
        if not self._widget.find(text, flags):
            if backwards:
                location = QtGui.QTextCursor.End
            else:
                location = QtGui.QTextCursor.Start
            cursor.movePosition(location, QtGui.QTextCursor.MoveAnchor)
            self._widget.setTextCursor(cursor)
            self._widget.find(text, flags)


def text_matches(case_sensitive, a, b):
    """Compare text with case sensitivity taken into account"""
    if case_sensitive:
        return a == b
    return a.lower() == b.lower()


class TextEditExtension(BaseTextEditExtension):
    def init(self):
        widget = self.widget
        widget.setAcceptRichText(False)

    def set_linebreak(self, brk):
        if brk:
            wrapmode = QtWidgets.QTextEdit.FixedColumnWidth
        else:
            wrapmode = QtWidgets.QTextEdit.NoWrap
        self.widget.setLineWrapMode(wrapmode)

    def set_textwidth(self, width):
        self.widget.setLineWrapColumnOrWidth(width)


class TextEdit(QtWidgets.QTextEdit):
    cursor_changed = Signal(int, int)
    leave = Signal()

    def __init__(self, parent=None, get_value=None, readonly=False):
        QtWidgets.QTextEdit.__init__(self, parent)
        self.ext = TextEditExtension(self, get_value, readonly)
        self.cursor_position = self.ext.cursor_position
        self.expandtab_enabled = False
        self.menu_actions = []

    def get(self):
        """Return the raw unicode value from Qt"""
        return self.ext.get()

    def value(self):
        """Return a safe value, e.g. a stripped value"""
        return self.ext.value()

    def set_cursor_position(self, position):
        """Set the cursor position"""
        cursor = self.textCursor()
        cursor.setPosition(position)
        self.setTextCursor(cursor)

    def set_value(self, value, block=False):
        self.ext.set_value(value, block=block)

    def selected_line(self):
        return self.ext.selected_line()

    def selected_text(self):
        """Return the selected text"""
        return self.ext.selected_text()

    def set_tabwidth(self, width):
        self.ext.set_tabwidth(width)

    def set_textwidth(self, width):
        self.ext.set_textwidth(width)

    def set_linebreak(self, brk):
        self.ext.set_linebreak(brk)

    def set_expandtab(self, value):
        self.expandtab_enabled = value

    def mousePressEvent(self, event):
        self.ext.mouse_press_event(event)
        super().mousePressEvent(event)

    def wheelEvent(self, event):
        """Disable control+wheelscroll text resizing"""
        if event.modifiers() & Qt.ControlModifier:
            event.ignore()
            return
        super().wheelEvent(event)

    def should_expandtab(self, event):
        return event.key() == Qt.Key_Tab and self.expandtab_enabled

    def expandtab(self):
        tabwidth = max(self.ext.tabwidth(), 1)
        cursor = self.textCursor()
        cursor.insertText(' ' * tabwidth)

    def create_context_menu(self, event_pos):
        """Create a custom context menu"""
        return self.ext.create_context_menu(event_pos)

    def contextMenuEvent(self, event):
        """Custom contextMenuEvent() for building our custom context menus"""
        self.ext.context_menu_event(event)

    def keyPressEvent(self, event):
        """Override keyPressEvent to handle tab expansion"""
        expandtab = self.should_expandtab(event)
        if expandtab:
            self.expandtab()
            event.accept()
        else:
            QtWidgets.QTextEdit.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        """Override keyReleaseEvent to special-case tab expansion"""
        expandtab = self.should_expandtab(event)
        if expandtab:
            event.ignore()
        else:
            QtWidgets.QTextEdit.keyReleaseEvent(self, event)


class TextEditCursorPosition:
    def __init__(self, widget, ext):
        self._widget = widget
        self._ext = ext
        widget.cursorPositionChanged.connect(self.emit)

    def emit(self):
        widget = self._widget
        ext = self._ext
        cursor = widget.textCursor()
        position = cursor.position()
        txt = widget.get()
        before = txt[:position]
        row = before.count('\n')
        line = before.split('\n')[row]
        col = cursor.columnNumber()
        col += line[:col].count('\t') * (ext.tabwidth() - 1)
        widget.cursor_changed.emit(row + 1, col)

    def reset(self):
        widget = self._widget
        cursor = widget.textCursor()
        cursor.setPosition(0)
        widget.setTextCursor(cursor)


class MonoTextEdit(PlainTextEdit):
    def __init__(self, context, parent=None, readonly=False):
        PlainTextEdit.__init__(self, parent=parent, readonly=readonly)
        self.setFont(qtutils.diff_font(context))


def get_value_hinted(widget):
    text = get_stripped(widget)
    hint = get(widget.hint)
    if text == hint:
        return ''
    return text


class HintWidget(QtCore.QObject):
    """Extend a widget to provide hint messages

    This primarily exists because setPlaceholderText() is only available
    in Qt5, so this class provides consistent behavior across versions.

    """

    def __init__(self, widget, hint):
        QtCore.QObject.__init__(self, widget)
        self._widget = widget
        self._hint = hint
        self._is_error = False

        self.modern = modern = hasattr(widget, 'setPlaceholderText')
        if modern:
            widget.setPlaceholderText(hint)

        # Palette for normal text
        QPalette = QtGui.QPalette
        palette = widget.palette()

        hint_color = palette.color(QPalette.Disabled, QPalette.Text)
        error_bg_color = QtGui.QColor(Qt.red).darker()
        error_fg_color = QtGui.QColor(Qt.white)

        hint_rgb = qtutils.rgb_css(hint_color)
        error_bg_rgb = qtutils.rgb_css(error_bg_color)
        error_fg_rgb = qtutils.rgb_css(error_fg_color)

        env = {
            'name': widget.__class__.__name__,
            'error_fg_rgb': error_fg_rgb,
            'error_bg_rgb': error_bg_rgb,
            'hint_rgb': hint_rgb,
        }

        self._default_style = ''

        self._hint_style = (
            """
            %(name)s {
                color: %(hint_rgb)s;
            }
        """
            % env
        )

        self._error_style = (
            """
            %(name)s {
                color: %(error_fg_rgb)s;
                background-color: %(error_bg_rgb)s;
            }
        """
            % env
        )

    def init(self):
        """Defered initialization"""
        if self.modern:
            self.widget().setPlaceholderText(self.value())
        else:
            self.widget().installEventFilter(self)
            self.enable(True)

    def widget(self):
        """Return the parent text widget"""
        return self._widget

    def active(self):
        """Return True when hint-mode is active"""
        return self.value() == get_stripped(self._widget)

    def value(self):
        """Return the current hint text"""
        return self._hint

    def set_error(self, is_error):
        """Enable/disable error mode"""
        self._is_error = is_error
        self.refresh()

    def set_value(self, hint):
        """Change the hint text"""
        if self.modern:
            self._hint = hint
            self._widget.setPlaceholderText(hint)
        else:
            # If hint-mode is currently active, re-activate it
            active = self.active()
            self._hint = hint
            if active or self.active():
                self.enable(True)

    def enable(self, enable):
        """Enable/disable hint-mode"""
        if not self.modern:
            if enable and self._hint:
                self._widget.set_value(self._hint, block=True)
                self._widget.cursor_position.reset()
            else:
                self._widget.clear()
        self._update_palette(enable)

    def refresh(self):
        """Update the palette to match the current mode"""
        self._update_palette(self.active())

    def _update_palette(self, hint):
        """Update to palette for normal/error/hint mode"""
        if self._is_error:
            style = self._error_style
        elif not self.modern and hint:
            style = self._hint_style
        else:
            style = self._default_style
        QtCore.QTimer.singleShot(
            0, lambda: utils.catch_runtime_error(self._widget.setStyleSheet, style)
        )

    def eventFilter(self, _obj, event):
        """Enable/disable hint-mode when focus changes"""
        etype = event.type()
        if etype == QtCore.QEvent.FocusIn:
            self.focus_in()
        elif etype == QtCore.QEvent.FocusOut:
            self.focus_out()
        return False

    def focus_in(self):
        """Disable hint-mode when focused"""
        widget = self.widget()
        if self.active():
            self.enable(False)
        widget.cursor_position.emit()

    def focus_out(self):
        """Re-enable hint-mode when losing focus"""
        widget = self.widget()
        valid, value = utils.catch_runtime_error(get, widget)
        if not valid:
            # The widget may have just been destroyed during application shutdown.
            # We're receiving a focusOut event but the widget can no longer be used.
            # This can be safely ignored.
            return
        if not value:
            self.enable(True)


class HintedPlainTextEdit(PlainTextEdit):
    """A hinted plain text edit"""

    def __init__(self, context, hint, parent=None, readonly=False):
        PlainTextEdit.__init__(
            self, parent=parent, get_value=get_value_hinted, readonly=readonly
        )
        self.hint = HintWidget(self, hint)
        self.hint.init()
        self.context = context
        self.setFont(qtutils.diff_font(context))
        self.set_tabwidth(prefs.tabwidth(context))
        # Refresh palettes when text changes
        # pylint: disable=no-member
        self.textChanged.connect(self.hint.refresh)
        self.set_mouse_zoom(context.cfg.get(prefs.MOUSE_ZOOM, default=True))

    def set_value(self, value, block=False):
        """Set the widget text or enable hint mode when empty"""
        if value or self.hint.modern:
            PlainTextEdit.set_value(self, value, block=block)
        else:
            self.hint.enable(True)


class HintedTextEdit(TextEdit):
    """A hinted text edit"""

    def __init__(self, context, hint, parent=None, readonly=False):
        TextEdit.__init__(
            self, parent=parent, get_value=get_value_hinted, readonly=readonly
        )
        self.context = context
        self.hint = HintWidget(self, hint)
        self.hint.init()
        # Refresh palettes when text changes
        # pylint: disable=no-member
        self.textChanged.connect(self.hint.refresh)
        self.setFont(qtutils.diff_font(context))

    def set_value(self, value, block=False):
        """Set the widget text or enable hint mode when empty"""
        if value or self.hint.modern:
            TextEdit.set_value(self, value, block=block)
        else:
            self.hint.enable(True)


def anchor_mode(select):
    """Return the QTextCursor mode to keep/discard the cursor selection"""
    if select:
        mode = QtGui.QTextCursor.KeepAnchor
    else:
        mode = QtGui.QTextCursor.MoveAnchor
    return mode


# The vim-like read-only text view


class VimMixin:
    def __init__(self, widget):
        self.widget = widget
        self.Base = widget.Base
        # Common vim/unix-ish keyboard actions
        self.add_navigation('End', hotkeys.GOTO_END)
        self.add_navigation('Up', hotkeys.MOVE_UP, shift=hotkeys.MOVE_UP_SHIFT)
        self.add_navigation('Down', hotkeys.MOVE_DOWN, shift=hotkeys.MOVE_DOWN_SHIFT)
        self.add_navigation('Left', hotkeys.MOVE_LEFT, shift=hotkeys.MOVE_LEFT_SHIFT)
        self.add_navigation('Right', hotkeys.MOVE_RIGHT, shift=hotkeys.MOVE_RIGHT_SHIFT)
        self.add_navigation('WordLeft', hotkeys.WORD_LEFT)
        self.add_navigation('WordRight', hotkeys.WORD_RIGHT)
        self.add_navigation('Start', hotkeys.GOTO_START)
        self.add_navigation('StartOfLine', hotkeys.START_OF_LINE)
        self.add_navigation('EndOfLine', hotkeys.END_OF_LINE)

        qtutils.add_action(
            widget,
            'PageUp',
            widget.page_up,
            hotkeys.SECONDARY_ACTION,
            hotkeys.TEXT_UP,
        )
        qtutils.add_action(
            widget,
            'PageDown',
            widget.page_down,
            hotkeys.PRIMARY_ACTION,
            hotkeys.TEXT_DOWN,
        )
        qtutils.add_action(
            widget,
            'SelectPageUp',
            lambda: widget.page_up(select=True),
            hotkeys.SELECT_BACK,
            hotkeys.SELECT_UP,
        )
        qtutils.add_action(
            widget,
            'SelectPageDown',
            lambda: widget.page_down(select=True),
            hotkeys.SELECT_FORWARD,
            hotkeys.SELECT_DOWN,
        )

    def add_navigation(self, name, hotkey, shift=None):
        """Add a hotkey along with a shift-variant"""
        widget = self.widget
        direction = getattr(QtGui.QTextCursor, name)
        qtutils.add_action(widget, name, lambda: self.move(direction), hotkey)
        if shift:
            qtutils.add_action(
                widget, 'Shift' + name, lambda: self.move(direction, select=True), shift
            )

    def move(self, direction, select=False, n=1):
        widget = self.widget
        cursor = widget.textCursor()
        mode = anchor_mode(select)
        for _ in range(n):
            if cursor.movePosition(direction, mode, 1):
                self.set_text_cursor(cursor)

    def page(self, offset, select=False):
        widget = self.widget
        rect = widget.cursorRect()
        x = rect.x()
        y = rect.y() + offset
        new_cursor = widget.cursorForPosition(QtCore.QPoint(x, y))
        if new_cursor is not None:
            cursor = widget.textCursor()
            mode = anchor_mode(select)
            cursor.setPosition(new_cursor.position(), mode)

            self.set_text_cursor(cursor)

    def page_down(self, select=False):
        widget = self.widget
        widget.page(widget.height() // 2, select=select)

    def page_up(self, select=False):
        widget = self.widget
        widget.page(-widget.height() // 2, select=select)

    def set_text_cursor(self, cursor):
        widget = self.widget
        widget.setTextCursor(cursor)
        widget.ensureCursorVisible()
        widget.viewport().update()

    def keyPressEvent(self, event):
        """Custom keyboard behaviors

        The leave() signal is emitted when `Up` is pressed and we're already
        at the beginning of the text.  This allows the parent widget to
        orchestrate some higher-level interaction, such as giving focus to
        another widget.

        When in the  middle of the first line and `Up` is pressed, the cursor
        is moved to the beginning of the line.

        """
        widget = self.widget
        if event.key() == Qt.Key_Up:
            cursor = widget.textCursor()
            position = cursor.position()
            if position == 0:
                # The cursor is at the beginning of the line.
                # Emit a signal so that the parent can e.g. change focus.
                widget.leave.emit()
            elif get(widget)[:position].count('\n') == 0:
                # The cursor is in the middle of the first line of text.
                # We can't go up ~ jump to the beginning of the line.
                # Select the text if shift is pressed.
                select = event.modifiers() & Qt.ShiftModifier
                mode = anchor_mode(select)
                cursor.movePosition(QtGui.QTextCursor.StartOfLine, mode)
                widget.setTextCursor(cursor)

        return self.Base.keyPressEvent(widget, event)


# pylint: disable=too-many-ancestors
class VimHintedPlainTextEdit(HintedPlainTextEdit):
    """HintedPlainTextEdit with vim hotkeys

    This can only be used in read-only mode.

    """

    Base = HintedPlainTextEdit
    Mixin = VimMixin

    def __init__(self, context, hint, parent=None):
        HintedPlainTextEdit.__init__(self, context, hint, parent=parent, readonly=True)
        self._mixin = self.Mixin(self)

    def move(self, direction, select=False, n=1):
        return self._mixin.page(direction, select=select, n=n)

    def page(self, offset, select=False):
        return self._mixin.page(offset, select=select)

    def page_up(self, select=False):
        return self._mixin.page_up(select=select)

    def page_down(self, select=False):
        return self._mixin.page_down(select=select)

    def keyPressEvent(self, event):
        return self._mixin.keyPressEvent(event)


# pylint: disable=too-many-ancestors
class VimTextEdit(MonoTextEdit):
    """Text viewer with vim-like hotkeys

    This can only be used in read-only mode.

    """

    Base = MonoTextEdit
    Mixin = VimMixin

    def __init__(self, context, parent=None, readonly=True):
        MonoTextEdit.__init__(self, context, parent=None, readonly=readonly)
        self._mixin = self.Mixin(self)

    def move(self, direction, select=False, n=1):
        return self._mixin.page(direction, select=select, n=n)

    def page(self, offset, select=False):
        return self._mixin.page(offset, select=select)

    def page_up(self, select=False):
        return self._mixin.page_up(select=select)

    def page_down(self, select=False):
        return self._mixin.page_down(select=select)

    def keyPressEvent(self, event):
        return self._mixin.keyPressEvent(event)


class HintedDefaultLineEdit(LineEdit):
    """A line edit with hint text"""

    def __init__(self, hint, tooltip=None, parent=None):
        LineEdit.__init__(self, parent=parent, get_value=get_value_hinted)
        if tooltip:
            self.setToolTip(tooltip)
        self.hint = HintWidget(self, hint)
        self.hint.init()
        # pylint: disable=no-member
        self.textChanged.connect(lambda text: self.hint.refresh())


class HintedLineEdit(HintedDefaultLineEdit):
    """A monospace line edit with hint text"""

    def __init__(self, context, hint, tooltip=None, parent=None):
        super().__init__(hint, tooltip=tooltip, parent=parent)
        self.setFont(qtutils.diff_font(context))


def text_dialog(context, text, title):
    """Show a wall of text in a dialog"""
    parent = qtutils.active_window()

    label = QtWidgets.QLabel(parent)
    label.setFont(qtutils.diff_font(context))
    label.setText(text)
    label.setMargin(defs.large_margin)
    text_flags = Qt.TextSelectableByKeyboard | Qt.TextSelectableByMouse
    label.setTextInteractionFlags(text_flags)

    widget = QtWidgets.QDialog(parent)
    widget.setWindowModality(Qt.WindowModal)
    widget.setWindowTitle(title)

    scroll = QtWidgets.QScrollArea()
    scroll.setWidget(label)

    layout = qtutils.hbox(defs.margin, defs.spacing, scroll)
    widget.setLayout(layout)

    qtutils.add_action(
        widget, N_('Close'), widget.accept, Qt.Key_Question, Qt.Key_Enter, Qt.Key_Return
    )
    widget.show()
    return widget


class VimTextBrowser(VimTextEdit):
    """Text viewer with line number annotations"""

    def __init__(self, context, parent=None, readonly=True):
        VimTextEdit.__init__(self, context, parent=parent, readonly=readonly)
        self.numbers = LineNumbers(self)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.numbers.refresh_size()


class TextDecorator(QtWidgets.QWidget):
    """Common functionality for providing line numbers in text widgets"""

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.editor = parent

        parent.blockCountChanged.connect(lambda x: self._refresh_viewport())
        parent.cursorPositionChanged.connect(self.refresh)
        parent.updateRequest.connect(self._refresh_rect)

    def refresh(self):
        """Refresh the numbers display"""
        rect = self.editor.viewport().rect()
        self._refresh_rect(rect, 0)

    def _refresh_rect(self, rect, dy):
        if dy:
            self.scroll(0, dy)
        else:
            self.update(0, rect.y(), self.width(), rect.height())

        if rect.contains(self.editor.viewport().rect()):
            self._refresh_viewport()

    def _refresh_viewport(self):
        self.editor.setViewportMargins(self.width_hint(), 0, 0, 0)

    def refresh_size(self):
        rect = self.editor.contentsRect()
        geom = QtCore.QRect(rect.left(), rect.top(), self.width_hint(), rect.height())
        self.setGeometry(geom)

    def sizeHint(self):
        return QtCore.QSize(self.width_hint(), 0)


class LineNumbers(TextDecorator):
    """Provide line numbers for QPlainTextEdit widgets"""

    def __init__(self, parent):
        TextDecorator.__init__(self, parent)
        self.highlight_line = -1

    def width_hint(self):
        document = self.editor.document()
        digits = int(math.log(max(1, document.blockCount()), 10)) + 2
        return defs.large_margin + self.fontMetrics().width('0') * digits

    def set_highlighted(self, line_number):
        """Set the line to highlight"""
        self.highlight_line = line_number

    def paintEvent(self, event):
        """Paint the line number"""
        QPalette = QtGui.QPalette
        painter = QtGui.QPainter(self)
        editor = self.editor
        palette = editor.palette()

        painter.fillRect(event.rect(), palette.color(QPalette.Base))

        content_offset = editor.contentOffset()
        block = editor.firstVisibleBlock()
        width = self.width()
        event_rect_bottom = event.rect().bottom()

        highlight = palette.color(QPalette.Highlight)
        highlighted_text = palette.color(QPalette.HighlightedText)
        disabled = palette.color(QPalette.Disabled, QPalette.Text)

        while block.isValid():
            block_geom = editor.blockBoundingGeometry(block)
            block_top = block_geom.translated(content_offset).top()
            if not block.isVisible() or block_top >= event_rect_bottom:
                break

            rect = block_geom.translated(content_offset).toRect()
            block_number = block.blockNumber()
            if block_number == self.highlight_line:
                painter.fillRect(rect.x(), rect.y(), width, rect.height(), highlight)
                painter.setPen(highlighted_text)
            else:
                painter.setPen(disabled)

            number = '%s' % (block_number + 1)
            painter.drawText(
                rect.x(),
                rect.y(),
                self.width() - defs.large_margin,
                rect.height(),
                Qt.AlignRight | Qt.AlignVCenter,
                number,
            )
            block = block.next()
