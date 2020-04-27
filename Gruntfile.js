module.exports = function (grunt) {
    'use strict';

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        // we could just concatenate everything, really
        // but we like to have it the complex way.
        // also, in this way we do not have to worry
        // about putting files in the correct order
        // (the dependency tree is walked by r.js)

        compass: {
            theming5: {
                options: {
                    sassDir: 'stylesheets/theming5',
                    cssDir: 'css',
                    outputStyle: 'compressed'
                },
            },
            bootstrap3: {
                options: {
                    sassDir: 'stylesheets/bootstrap',
                    cssDir: 'css/',
                    outputStyle: 'compressed'
                },
            },
            ulearn: {
                options: {
                    sassDir: 'stylesheets/ulearn',
                    cssDir: 'css/',
                    outputStyle: 'compressed'
                },
            },
            ulearn_backend: {
                options: {
                    sassDir: 'stylesheets/ulearn_backend',
                    cssDir: 'css/',
                    outputStyle: 'compressed'
                },
            }
        },
        concat: {
            options: {
                separator: '',
            },
            theming5: {
                src: ['css/theming5.css'],
                dest: 'css/theming5.min.css',
            },
            bootstrap3: {
                src: ['css/bootstrap.css'],
                dest: 'css/bootstrap3.min.css',
            },
            ulearn: {
                src: ['../../../../../../ulearn5.js/ulearn5/js/components/angular-ui-select/dist/select.css',
                '../../../../../../ulearn5.js/ulearn5/js/components/selectize/dist/css/selectize.default.css',
                '../../../../../../ulearn5.js/ulearn5/js/components/selectize/dist/css/selectize.bootstrap2.css',
                '../../../../../../ulearn5.js/ulearn5/js/components/ngDialog/css/ngDialog.css',
                '../../../../../../ulearn5.js/ulearn5/js/components/ngDialog/css/ngDialog-theme-default.css',
                '../../../../../../ulearn5.js/ulearn5/js/components/ngDialog/css/ngDialog-theme-plain.css',
                '../../../../../../ulearn5.js/ulearn5/js/components/sweetalert/lib/sweet-alert.css',
                '../../../../../../ulearn5.js/ulearn5/js/components/v-modal/dist/v-modal.css',
                'css/ulearn.css'],
                dest: 'css/ulearn-concat.css',
            },
            ulearn_backend: {
                src: ['css/ulearn_backend.css'],
                dest: 'css/ulearn_backend.min.css',
            }
        },
        cssmin: {
            target : {
                src : ["css/ulearn-concat.css"],
                dest : "css/ulearn.min.css"
            }
        },
        watch: {
            theming5: {
                files: [
                    'stylesheets/theming5/*.scss',
                    'stylesheets/theming5.scss'
                ],
                tasks: ['compass:theming5', 'concat:theming5'] //concat here only for renaming
            },
            bootstrap3:  {
                files: [
                    'stylesheets/bootstrap/*.scss',
                    'stylesheets/bootstrap/mixins/*.scss',
                    'stylesheets/bootstrap.scss',
                ],
                tasks: ['compass:bootstrap3', 'concat:bootstrap3'] //concat here only for renaming
            },
            ulearn: {
                files: [
                    'stylesheets/ulearn/*.scss',
                    'stylesheets/ulearn.scss',
                    '!stylesheets/ulearn/*backend.scss'
                ],
                tasks: ['compass:ulearn', 'concat:ulearn', 'cssmin']
            },
            ulearn_backend: {
                files: [
                    'stylesheets/ulearn/*backend.scss'
                ],
                tasks: ['compass:ulearn', 'concat:ulearn', 'cssmin', 'compass:ulearn_backend', 'concat:ulearn_backend']
            }
        },
        uglify: {
            main: {
                files: {
                    'javascripts/theming5.min.js': 'javascripts/theming5.js',
                    'javascripts/users_communities.min.js': 'javascripts/users_communities.js'
                }
            }
        },
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
    grunt.loadNpmTasks('grunt-contrib-compass');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-cssmin');
    grunt.loadNpmTasks('grunt-contrib-uglify');

    // CWD to theme folder
    grunt.file.setBase('./src/ulearn5/theme/theme/assets');

    // Registered tasks: grunt watch
    grunt.registerTask('default', ["browserSync:plone", "watch"]);
    grunt.registerTask('bsync', ["browserSync:html", "watch"]);
    grunt.registerTask('plone-bsync', ["browserSync:plone", "watch"]);
    grunt.registerTask('minify', ['uglify']);
};
