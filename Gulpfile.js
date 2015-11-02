var gulp = require('gulp');
var sass = require('gulp-sass');
var sourceMaps = require('gulp-sourcemaps');

var config = {
    paths : {
        sass      : './myDmarcApp/static/sass',
        css       : './myDmarcApp/static/css',
        fonts     : './myDmarcApp/static/fonts',
        vendor    : './myDmarcApp/static/vendor',
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

//Create css file from scss
gulp.task('styles', function() {
    return gulp.src(config.paths.sass + '/mydmarc.scss')
        .pipe(sourceMaps.init())
        .pipe(sass(sassOptions).on('error', sass.logError))
        .pipe(sourceMaps.write('.'))
        .pipe(gulp.dest(config.paths.css))
});

//Copy bootstrap fonts to generic public fonts folder
gulp.task('fonts', function() {
    return gulp.src(config.paths.vendor + '/bootstrap-sass-3.3.5/assets/fonts/**/*')
    .pipe(gulp.dest(config.paths.fonts));
})

//Watch task
gulp.task('default', function() {
    return gulp.watch(config.paths.sass + '/**/*.scss', ['styles', 'fonts']);
});