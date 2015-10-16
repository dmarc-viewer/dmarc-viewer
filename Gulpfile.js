var gulp = require('gulp');
var sass = require('gulp-sass');
var sourcemaps = require('gulp-sourcemaps');


var input = './myDmarcApp/static/sass/**/*.scss';
var output = './myDmarcApp/static/css/';

var sassOptions = {
  errLogToConsole: true,
  outputStyle: 'expanded'
};

gulp.task('sass', function() {
    return gulp.src(input)
        .pipe(sourcemaps.init())
        .pipe(sass(sassOptions).on('error', sass.logError))
        .pipe(sourcemaps.write())
        .pipe(gulp.dest(output))
});

//Watch task
gulp.task('default',function() {
    return gulp.watch(input, ['sass']);
});