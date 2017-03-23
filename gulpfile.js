var gulp = require('gulp'),
 watch = require('gulp-watch'),
 livereload = require('gulp-livereload'),
 beautify = require('gulp-beautify'),
 uglify = require('gulp-uglify'),
 sass = require('gulp-sass');

 function errorLog(error){
     console.error.bind(error);
     this.emit('end');
 }



gulp.task('beautify', function () {
gulp.src('./color_nerds_blog/static/Js/*.js')
    .pipe(beautify({indent_size: 2}))
    .on('error', errorLog)
    .pipe(gulp.dest('./color_nerds_blog/'));
});

gulp.task('sass', function () {
  return gulp.src('./color_nerds_blog/static/Sass/**/*.scss')
    .pipe(sass().on('error', errorLog))
    .pipe(gulp.dest('./color_nerds_blog/css'))
    .pipe(livereload());
});
 
gulp.task('watch', function () {
  livereload.server;
  livereload.listen();
  gulp.watch('./color_nerds_blog/static/Js/*.js', ['beautify'] );
  gulp.watch('./color_nerds_blog/static/Sass/*.sass', ['sass'] );
});

 
 gulp.task('default', ['watch'])