
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
    Frontend dependency task runners to

    - Compile SCSS to CSS (website/static/sass)
    - Vendorize fonts (node_modules)
    - Create dist files
        - 3rd party CSS (node_modules)
        - 3rd party JS (node_modules)
        - local CSS (website/static/css)
        - local JS (website/static/js)


    3rd party dependencies are defined in `package.json` and can be installed
    using npm like so:

        npm install


    3rd party dependencies are always served from `dist` (the latest minified
    concatenated version should be checked into vcs).
    Creating new `dist` files is only necessary when dependencies are
    updated/added/removed.

    3rd party fonts are served from `website/static/fonts` and are also
    checked into vcs. (AFAIK there is no obvious way to create a `dist` version
    from fonts).

    Local frontend code is served either from `dist` (the latest minified
    concatenated version should be checked into vcs) or non-minified from
    `website/static/js` and `website/static/css` when the Django setting
    `settings.TEMPLATE_SETTINGS.use_dist` is `False`

    Change local frontend code in `website/static/js` and
    `website/static/sass` only (sass code is compiled to css code with an extra
    task runner).

<Usage>
    Task runners can be invoked from the command line, e.g.:
    ```
    gulp create-dist
    gulp create-dist-js
    gulp create-dist-css
    gulp create-dist-js-node-modules
    gulp create-dist-css-node-modules
    gulp copy-fonts
    gulp compile-scss
    ```


*****************************************************************/



var gulp = require('gulp');
var gulpSass = require('gulp-sass');
var gulpConcat = require('gulp-concat');
var gulpUglifyJs = require('gulp-uglify');
var gulpCleanCss = require('gulp-clean-css');
var gulpSourceMaps = require('gulp-sourcemaps');

/*
 * List of all 3rd party and non-3rd party frontend dependencies, i.e.
 * CSS/SCSS, JavaScript and fonts.
 * Note: Requires dependencies installed in `node_modules`.
 */
var paths = {
    css: [
        'website/static/css/dmarc_viewer.css'
    ],
    js: [
        'website/static/js/main.js',
        'website/static/js/editor.js',
        'website/static/js/analysis.js',
        'website/static/js/d3.legend.js'
    ],
    scss: [
        'website/static/sass/dmarc_viewer.scss'
    ],
    scss_node_modules: [
        'node_modules/bootstrap-sass/assets/stylesheets',
        'node_modules/bootstrap-colorpicker/src/sass',
    ],
    css_node_modules: [
        'node_modules/selectize/dist/css/selectize.bootstrap3.css',
        'node_modules/bootstrap-datepicker/dist/css/bootstrap-datepicker3.css',
        'node_modules/bootstrap-colorpicker/dist/css/bootstrap-colorpicker.css',
        'node_modules/datatables.net-bs/css/dataTables.bootstrap.css',
        'node_modules/datatables.net-responsive-bs/css/responsive.bootstrap.css'
    ],
    js_node_modules: [
        'node_modules/jquery/dist/jquery.js',
        'node_modules/bootstrap-sass/assets/javascripts/bootstrap.js',
        'node_modules/sortablejs/Sortable.js',
        'node_modules/selectize/dist/js/standalone/selectize.js',
        'node_modules/bootstrap-colorpicker/dist/js/bootstrap-colorpicker.js',
        'node_modules/bootstrap-datepicker/js/bootstrap-datepicker.js',
        'node_modules/datatables.net/js/jquery.dataTables.js',
        'node_modules/datatables.net-bs/js/dataTables.bootstrap.js',
        'node_modules/datatables.net-responsive/js/dataTables.responsive.js',
        'node_modules/d3/d3.js',
        'node_modules/topojson/dist/topojson.js',
        'node_modules/datamaps/dist/datamaps.all.js',
    ],
    fonts_node_modules: [
        'node_modules/bootstrap-sass/assets/fonts/**/*'
    ]
}

/*
 * Helper function to minify and concatenate the files in the passed list of
 *`src_paths` using the passed `minifier` (e.g. `gulpClassCss` for CSS,
 * or `gulpUglify` for JS) and writes the resulting file to
 * "website/static/dist/dmarc_viewer.dist" + `suffix`.
 */
function _create_dist(src_paths, minifier, suffix) {
    return gulp.src(src_paths)
        .pipe(minifier())
        .pipe(gulpConcat('dmarc_viewer.dist' + suffix))
        .pipe(gulp.dest('website/static/dist'));
}


/*
 * Tasks to minify and concatenate third party and non-third party
 * CSS and JS, copying them to `static/dist`.
 * Note: Requires dependencies installed in `node_modules`.
 */
gulp.task('create-dist-js', function(){
    return _create_dist(paths.js, gulpUglifyJs,'.js')
});
gulp.task('create-dist-css', function(){
    return _create_dist(paths.css, gulpCleanCss, '.css')
});

// TODO: Do we need source maps for third party code? Might be nice
// for debugging
gulp.task('create-dist-js-node-modules', function(){
    return _create_dist(paths.js_node_modules, gulpUglifyJs, '.npm.js')
});
gulp.task('create-dist-css-node-modules', function(){
    return _create_dist(paths.css_node_modules, gulpCleanCss, '.npm.css')
});

/*
 * Task to copy Bootstraps fonts from `node_modules` to `static/fonts`
 */
gulp.task('copy-fonts', function() {
    return gulp.src(paths.fonts_node_modules)
        .pipe(gulp.dest('website/static/fonts/'));
});

/*
 * Copies 3rd party and non-3rd party css, js and fonts to dist.
 * Note: This does not compile scss, so make sure to run the `compile-scss`
 * task first if you have changed any scss files and want them in the minified
 * dist.
 */
gulp.task('create-dist', [
    'copy-fonts',
    'create-dist-js-node-modules',
    'create-dist-css-node-modules',
    'create-dist-js',
    'create-dist-css'
    ]
);

/*
 * Task to compile SCSS files and copy it to `static/css` (with sourcemap).
 * Note: `includePaths` define 3rd party SCSS files that are included (by name)
 * in the main scss file that gets compiled.
 */
gulp.task('compile-scss', function() {
    return gulp.src(paths.scss)
        .pipe(gulpSourceMaps.init())
        .pipe(gulpSass({
            errLogToConsole: true,
            outputStyle: 'expanded',
            includePaths: paths.scss_node_modules,
        }).on('error', gulpSass.logError))
        .pipe(gulpSourceMaps.write('.'))
        .pipe(gulp.dest('website/static/css'))
});

/*
 * Watcher task to compile to SCSS to CSS if the main SCSS file changes
 */
gulp.task('watch-scss', function() {
    return gulp.watch(paths.scss, ['compile-scss'])
});
