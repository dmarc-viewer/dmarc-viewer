var gulp = require('gulp');
var sass = require('gulp-sass');
var sourceMaps = require('gulp-sourcemaps');
// var cssImport = require('gulp-cssimport');

var config = {
    paths : {
        sass   : './myDmarcApp/static/sass',
        css    : './myDmarcApp/static/css',
        vendor : './myDmarcApp/static/vendor',
    }
}

var sassOptions = {
  errLogToConsole: true,
  outputStyle: 'expanded',
  includePaths: [
                 config.paths.sass,
                 config.paths.vendor + '/bootstrap-sass-3.3.5/assets/stylesheets',
             ]
};

gulp.task('sass', function() {
    return gulp.src(config.paths.sass + '/**/*.scss')
        .pipe(sourceMaps.init())
        .pipe(sass(sassOptions).on('error', sass.logError))
        // .pipe(cssImport())
        .pipe(sourceMaps.write())
        .pipe(gulp.dest(config.paths.css))
});

//Watch task
gulp.task('default', function() {
    return gulp.watch(config.paths.sass + '/**/*.scss', ['sass']);
});