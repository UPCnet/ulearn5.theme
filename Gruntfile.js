module.exports = function (grunt) {
    'use strict';

    var uglify_options = {
        sourceMap: true };

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        // we could just concatenate everything, really
        // but we like to have it the complex way.
        // also, in this way we do not have to worry
        // about putting files in the correct order
        // (the dependency tree is walked by r.js)

        compass: {
            upc: {
                options: {
                    sassDir: 'stylesheets/upc',
                    cssDir: 'css',
                    outputStyle: 'compressed'
                },
                files: {
                    'css/upc.css': 'stylesheets/upc.scss'
                }
            },
            homeupc: {
                options: {
                    sassDir: 'stylesheets',
                    cssDir: 'css',
                    outputStyle: 'compressed'
                },
                files: {
                    'css/upcnet.css': 'stylesheets/upcnet.scss',
                    'css/bootstrap.css': 'stylesheets/bootstrap.scss'
                }
            },
            ulearn: {
                options: {
                    sassDir: 'stylesheets/ulearn',
                    cssDir: 'css',
                    outputStyle: 'compressed'
                },
                files: {
                    'css/ulearn.css': 'stylesheets/ulearn.scss'
                }
            }
        },
        concat: {
            options: {
                separator: '',
            },
            dist: {
                src: ['css/bootstrap.css', 'css/upcnet.css'],
                dest: 'css/homeupc-compiled.css',
            },
        },
        watch: {
            upc: {
                files: [
                    'stylesheets/upc/*.scss',
                    'stylesheets/upc.scss'
                ],
                tasks: ['compass:upc']
            },
            homeupc:  {
                files: [
                    'stylesheets/bootstrap/*.scss',
                    'stylesheets/bootstrap/mixins/*.scss',
                    'stylesheets/bootstrap.scss',
                    'stylesheets/upcnet.scss',
                ],
                tasks: ['compass:homeupc', 'concat']
            },
            ulearn: {
                files: [
                    'stylesheets/ulearn/*.scss',
                    'stylesheets/ulearn.scss'
                ],
                tasks: ['compass:ulearn']
            }
        },

        // uglify: {
        //     main: {
        //         files: {
        //             'dist/homeupc.min.js': ['javascripts/upcnet.js'],
        //             'dist/search.min.js': ['javascripts/search.js']
        //         }
        //     }
        // },

        browserSync: {
            plone: {
                bsFiles: {
                    src : [
                      'css/*.css'
                    ]
                },
                options: {
                    watchTask: true,
                    debugInfo: true,
                    proxy: "localhost:8080/Plone",
                    reloadDelay: 3000,
                    // reloadDebounce: 2000,
                    online: true
                }
            }
        }
    });

    // grunt.loadTasks('tasks');
    grunt.loadNpmTasks('grunt-browser-sync');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-compass');
    grunt.loadNpmTasks('grunt-contrib-concat');

    // CWD to theme folder
    grunt.file.setBase('./src/ulearn5/theme/theme/assets');

    grunt.registerTask('default', ["browserSync:plone", "watch"]);
    grunt.registerTask('bsync', ["browserSync:html", "watch"]);
    grunt.registerTask('plone-bsync', ["browserSync:plone", "watch"]);
    grunt.registerTask('minify', ['uglify']);
};
