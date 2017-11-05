
/*****************************************************************
<File Name>
    Gulpfile.js

<Author>
    Lukas Puehringer <luk.puehringer@gmail.com>

<Started>
    July 22, 2015

<Copyright>
    See LICENSE for licensing information.

<Purpose>
    Provides task runners to copy JS, CSS and fonts from `node_modules`
    to a directory where Django can serve it from and to compile sass into CSS.

    Todo:
        - Documentation/Usage instructions
            - Readme's `contribution` section should point here

        - Separate tasks for 3rd party and non-3rd party sources
            - non-3rd party should not be copied to vendor
            - watcher only for sass compilation

        - Find a way to include fonts in minified dist script


*****************************************************************/


var gulp = require('gulp');
var sass = require('gulp-sass');
var concat = require('gulp-concat');
var uglifyJs = require('gulp-uglify');
var minifyCss = require('gulp-minify-css');
var sourceMaps = require('gulp-sourcemaps');

var config = {
    paths : {
        sass      : 'website/static/sass',
        css       : 'website/static/css',
        js        : 'website/static/js',
        fonts     : 'website/static/fonts',
        vendor    : 'website/static/vendor',
    }
}

var sassOptions = {
  errLogToConsole: true,
  outputStyle: 'expanded',
  includePaths: [
                 config.paths.sass,
                 'node_modules/bootstrap-sass/assets/stylesheets',
                 'node_modules/bootstrap-colorpicker/src/sass/',
             ]
};

// All JS files
var jsFiles = [
    'node_modules/jquery/dist/jquery.js',
    'node_modules/bootstrap-sass/assets/javascripts/bootstrap.js',
    'node_modules/sortablejs/Sortable.js',
    'node_modules/selectize/dist/js/standalone/selectize.js',
    'node_modules/bootstrap-colorpicker/src/js/colorpicker-color.js',
    'node_modules/bootstrap-datepicker/js/bootstrap-datepicker.js',
    'node_modules/datatables.net/js/jquery.dataTables.js',
    'node_modules/datatables.net-bs/js/dataTables.bootstrap.js',
    'node_modules/datatables.net-responsive/js/dataTables.responsive.js',
    'node_modules/d3/d3.js',
    'node_modules/topojson/dist/topojson.js',
    'node_modules/datamaps/dist/datamaps.all.js',
    config.paths.js + '/main.js',
    config.paths.js + '/editor.js',
    config.paths.js + '/analysis.js',
    config.paths.js + '/d3.legend.js'];

var cssFiles = [
    'node_modules/selectize/dist/css/selectize.bootstrap3.css',
    'node_modules/bootstrap-datepicker/dist/css/bootstrap-datepicker3.css',
    'node_modules/bootstrap-colorpicker/dist/css/bootstrap-colorpicker.css',
    'node_modules/datatables.net-bs/css/dataTables.bootstrap.css',
    'node_modules/datatables.net-responsive-bs/css/responsive.bootstrap.css',
    config.paths.css + '/dmarc_viewer.css'
]

//Create css file from scss
gulp.task('styles', function() {
    return gulp.src(config.paths.sass + '/dmarc_viewer.scss')
        .pipe(sourceMaps.init())
        .pipe(sass(sassOptions).on('error', sass.logError))
        .pipe(sourceMaps.write('.'))
        .pipe(gulp.dest(config.paths.css))
});

// Vendorize bootstrap fonts from node_modules
gulp.task('vendor-fonts', function() {
    return gulp.src('node_modules/bootstrap-sass/assets/fonts/**/*')
    .pipe(gulp.dest(config.paths.fonts));
});

// Vendorize CSS files from node_modules
gulp.task('vendor-js', function() {
    return gulp.src(jsFiles)
    .pipe(gulp.dest(config.paths.vendor));
});

// Vendorize CSS files from node_modules
gulp.task('vendor-css', function() {
    return gulp.src(cssFiles)
    .pipe(gulp.dest(config.paths.vendor));
});

// Concat and Minify/Uglify JS
gulp.task('min-js', function(){
    return gulp.src(jsFiles)
        .pipe(uglifyJs())
        .pipe(concat('dmarc_viewer.dist.min.js'))
        .pipe(gulp.dest(config.paths.js));
});

// Concat and Minify/Uglify CSS
gulp.task('min-css', function(){
    return gulp.src(cssFiles)
        .pipe(minifyCss())
        .pipe(concat('dmarc_viewer.dist.min.css'))
        .pipe(gulp.dest(config.paths.css));
});

//Watch task
gulp.task('default', function() {
    return gulp.watch(config.paths.sass + '/**/*.scss', ['styles', 'vendor-fonts', 'vendor-js', 'vendor-css']);
});