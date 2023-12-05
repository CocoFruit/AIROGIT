const {spawnSync} = require('child_process');
const path = require('path');
const tmp = require('tmp');
const glob = require('glob');

const {
  ReactVersion,
@@ -235,19 +236,28 @@ function processExperimental(buildDir, version) {
    );
  }

  if (fs.existsSync(buildDir + '/facebook-www')) {
    const hash = crypto.createHash('sha1');
    for (const fileName of fs.readdirSync(buildDir + '/facebook-www').sort()) {
      const filePath = buildDir + '/facebook-www/' + fileName;
  const facebookWwwDir = path.join(buildDir, 'facebook-www');
  if (fs.existsSync(facebookWwwDir)) {
    for (const fileName of fs.readdirSync(facebookWwwDir).sort()) {
      const filePath = path.join(facebookWwwDir, fileName);
      const stats = fs.statSync(filePath);
      if (!stats.isDirectory()) {
        hash.update(fs.readFileSync(filePath));
        fs.renameSync(filePath, filePath.replace('.js', '.modern.js'));
      }
    }
    const contentHash = hashJSFilesInDirectory(facebookWwwDir);
    updatePlaceholderReactVersionInCompiledArtifacts(
      buildDir + '/facebook-www',
      ReactVersion + '-www-modern-' + hash.digest('hex').slice(0, 8)
      facebookWwwDir,
      ReactVersion + '-www-modern-' + contentHash
    );
  }

  const facebookReactNativeDir = path.join(buildDir, 'facebook-react-native');
  if (fs.existsSync(facebookReactNativeDir)) {
    const contentHash = hashJSFilesInDirectory(facebookReactNativeDir);
    updatePlaceholderReactVersionInCompiledArtifacts(
      facebookReactNativeDir,
      ReactVersion + '-react-native-' + contentHash
    );
  }

@@ -346,6 +356,14 @@ function updatePackageVersions(
  }
}

function hashJSFilesInDirectory(directory) {
  const hash = crypto.createHash('sha1');
  for (const filePath of glob.sync(directory + '/**/*.js').sort()) {
    hash.update(fs.readFileSync(filePath));
  }
  return hash.digest('hex').slice(0, 8);
}

function updatePlaceholderReactVersionInCompiledArtifacts(
  artifactsDirectory,
  newVersion