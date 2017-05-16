var gulp = require('gulp');
var watch=require('gulp-watch');
var connect = require('gulp-connect');
// var jshint=require('gulp-jshint');

gulp.task('webserver',function () {
  connect.server({
    port:8000,
    livereload:true,
  });
});

gulp.task('jsLint', function () {
    gulp.src('./js/*.js') // path to your files
    .pipe(jshint())
    .pipe(jshint.reporter()); // Dump results
});


gulp.task('livereload',function () {
  watch(['js/*.js']).pipe(jshint()).pipe(jshint.reporter());
  watch(['css/*.css','js/*.js','*.html']).pipe(connect.reload());
});

gulp.task('default',['webserver','livereload']);