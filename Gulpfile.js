var gulp = require('gulp');
var sass = require('gulp-sass');
var concat = require('gulp-concat');
var uglifyJs = require('gulp-uglify');
var minifyCss = require('gulp-minify-css');
var sourceMaps = require('gulp-sourcemaps');

var config = {
    paths : {
        sass      : './website/static/sass',
        css       : './website/static/css',
        js        : './website/static/js',
        fonts     : './website/static/fonts',
        vendor    : './website/static/vendor',
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
    return gulp.src(config.paths.sass + '/dmarc_viewer.scss')
        .pipe(sourceMaps.init())
        .pipe(sass(sassOptions).on('error', sass.logError))
        .pipe(sourceMaps.write('.'))
        .pipe(gulp.dest(config.paths.css))
});

//Copy bootstrap fonts to generic public fonts folder
gulp.task('fonts', function() {
    return gulp.src(config.paths.vendor + '/bootstrap-sass-3.3.5/assets/fonts/**/*')
    .pipe(gulp.dest(config.paths.fonts));
});


// All JS files
var jsFiles = [
    config.paths.vendor +  '/jquery/jquery-1.11.3.min.js',
    config.paths.vendor +  '/jquery/jquery-migrate-1.2.1.min.js',
    config.paths.vendor +  '/bootstrap-sass-3.3.5/assets/javascripts/bootstrap.js',
    config.paths.vendor +  '/Sortable/Sortable.js',
    config.paths.vendor +  '/selectize/js/standalone/selectize.min.js',
    config.paths.vendor +  '/bootstrap-colorpicker/js/bootstrap-colorpicker.js',
    config.paths.vendor +  '/bootstrap-datepicker/dist/js/bootstrap-datepicker.js',
    config.paths.vendor +  '/DataTables-1.10.9/js/jquery.dataTables.js',
    config.paths.vendor +  '/DataTables-1.10.9/js/dataTables.bootstrap.js',
    config.paths.vendor +  '/DataTables-1.10.9/js/dataTables.responsive.min.js',
    config.paths.vendor +  '/d3/d3.js',
    config.paths.vendor +  '/topojson/topojson.js',
    config.paths.vendor +  '/datamaps/dist/datamaps.world.js',
    '../venv/lib/python2.7/site-packages/djangoformsetjs/static/js/jquery.formset.js', //This could be somewhere else
    config.paths.js + '/main.js',
    config.paths.js + '/editor.js',
    config.paths.js + '/analysis.js',
    config.paths.js + '/d3.legend.js'];

// Concat and Minify/Uglify JS
gulp.task('min-js', function(){
    return gulp.src(jsFiles)
        .pipe(uglifyJs())
        .pipe(concat('dmarc_viewer.dist.min.js'))
        .pipe(gulp.dest(config.paths.js));
});


var cssFiles = [
    config.paths.vendor + '/selectize/css/selectize.css',
    config.paths.vendor + '/selectize/css/selectize.default.css',
    config.paths.vendor + '/selectize/css/selectize.legacy.css',
    config.paths.vendor + '/selectize/css/selectize.bootstrap3.css',
    config.paths.vendor + '/bootstrap-colorpicker/css/bootstrap-colorpicker.css',
    config.paths.vendor + '/bootstrap-datepicker/dist/css/bootstrap-datepicker3.css',
    config.paths.vendor + '/DataTables-1.10.9/css/dataTables.bootstrap.css',
    config.paths.vendor + '/DataTables-1.10.9/css/responsive.bootstrap.min.css',
    config.paths.css + '/dmarc_viewer.css'
]

// Concat and Minify/Uglify CSS
gulp.task('min-css', function(){
    return gulp.src(cssFiles)
        .pipe(minifyCss())
        .pipe(concat('dmarc_viewer.dist.min.css'))
        .pipe(gulp.dest(config.paths.css));
});

//Watch task
gulp.task('default', function() {
    return gulp.watch(config.paths.sass + '/**/*.scss', ['styles', 'fonts']);
});