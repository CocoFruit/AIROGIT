import matplotlib.pyplot as plt
import numpy as np
# Define data
groups = ['Microsoft JARVIS', 'Facebook React', 'Audacity', 
          'Microsoft Calculator', 'Null Array AutoSploit', 'Null Array AutoSploit 2',
          'Microsoft PowerToys', 'JJTech0130 pypush', 'CocoFruit AIROGIT']
human_scores = [10, 14, 10, 8, 8, 8, 20, 10, 8]
ai_scores = [18, 16, 18, 16, 16, 16, 16, 16, 18]

print(len(groups), len(human_scores), len(ai_scores))

# Calculate total scores
total_human_score = sum(human_scores)
total_ai_score = sum(ai_scores)

# Combine data for boxplot
all_data = [human_scores, ai_scores]

# Labels for x-axis
labels = ['Human Scores', 'AI Scores']

# Create figure and axes
fig, ax1 = plt.subplots(figsize=(7, 6))
fig2, ax2 = plt.subplots(figsize=(7, 6))
fig3, ax3 = plt.subplots(figsize=(7, 6))

# Create boxplot
bplot1 = ax1.boxplot(all_data,
                     vert=True,        # Vertical box alignment
                     patch_artist=True,  # Fill with color
                     labels=labels)    # Label x-ticks
ax1.set_title('Comparison of Human and AI Scores')

# Define colors for the boxes
colors = ['pink', 'lightblue']

# Assign colors to the boxes
for patch, color in zip(bplot1['boxes'], colors):
    patch.set_facecolor(color)

# Add horizontal grid lines
ax1.yaxis.grid(True)
ax1.set_xlabel('Commiter')
ax1.set_ylabel('Scores')

# Create bar chart
bar_width = 0.35
index = range(len(groups))
ax2.bar(index, human_scores, bar_width, label='Human Scores')
ax2.bar([i + bar_width for i in index], ai_scores, bar_width, label='AI Scores')

ax2.set_xlabel('Commit Repositories')
ax2.set_ylabel('Scores')
ax2.set_title('Comparison of Human and AI Scores')
ax2.set_xticks([i + bar_width / 2 for i in index])
ax2.set_xticklabels(groups, rotation=45, ha='right')
ax2.legend()

# Create Violin plot
ax3.violinplot(all_data, showmeans=True, showmedians=True)
ax3.set_xticks([1, 2], labels)
ax3.set_title('Comparison of Human and AI Scores')
ax3.set_xlabel('Commiter')
ax3.set_ylabel('Scores')


fig.tight_layout()
fig2.tight_layout()
fig3.tight_layout()

# Save individual plots
fig.savefig('boxplot.svg')
fig2.savefig('barplot.svg')
fig3.savefig('violinplot.svg')
fig.savefig('boxplot.png')
fig2.savefig('barplot.png')
fig3.savefig('violinplot.png')
# Show the plots
# plt.show()

# show the barplot and the violinplot side by side
fig, ax = plt.subplots(1, 2, figsize=(10, 6))
ax[0].bar(index, human_scores, bar_width, label='Human Scores')
ax[0].bar([i + bar_width for i in index], ai_scores, bar_width, label='AI Scores')
ax[0].set_xlabel('Commit Repositories')
ax[0].set_ylabel('Scores')
ax[0].set_title('Comparison of Human and AI Scores')
ax[0].set_xticks([i + bar_width / 2 for i in index])
ax[0].set_xticklabels(groups, rotation=45, ha='right')
ax[0].legend()

ax[1].violinplot(all_data, showmeans=True, showmedians=True)
ax[1].set_xticks([1, 2], labels)
ax[1].set_title('Comparison of Human and AI Scores')
ax[1].set_xlabel('Commiter')
ax[1].set_ylabel('Scores')

# show
plt.tight_layout()
plt.show()

# Save the combined plot

fig.savefig('combinedplot.svg')
fig.savefig('combinedplot.png')
