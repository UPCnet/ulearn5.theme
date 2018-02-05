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
            upc: {
                options: {
                    sassDir: 'stylesheets/upc',
                    cssDir: 'css',
                    outputStyle: 'compressed'
                },
                files: {
                    'css/upc.css': 'stylesheets/upc/upc.scss'
                }
            },
            homeupc: {
                options: {
                    sassDir: 'stylesheets/bootstrap',
                    cssDir: 'css',
                    outputStyle: 'compressed'
                },
                files: {
                    'css/upcnet.css': 'stylesheets/bootstrap/upcnet.scss',
                    'css/bootstrap.css': 'stylesheets/bootstrap/bootstrap.scss'
                }
            },
            ulearn: {
                options: {
                    sassDir: 'stylesheets/ulearn',
                    cssDir: 'css/ulearn/',
                    outputStyle: 'compressed'
                },
                files: {
                    'css/ulearn/ulearn.css': 'stylesheets/ulearn/ulearn.scss'
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
            ulearn: {
                src: ['../../../../../../ulearn5.js/ulearn5/js/components/angular-ui-select/dist/select.css',
                "../../../../../../ulearn5.js/ulearn5/js/components/selectize/dist/css/selectize.default.css",
                "../../../../../../ulearn5.js/ulearn5/js/components/selectize/dist/css/selectize.bootstrap2.css",
                '../../../../../../ulearn5.js/ulearn5/js/components/angular-datatables/dist/plugins/bootstrap/datatables.bootstrap.css',
                '../../../../../../ulearn5.js/ulearn5/js/components/ngDialog/css/ngDialog.css',
                '../../../../../../ulearn5.js/ulearn5/js/components/ngDialog/css/ngDialog-theme-default.css',
                '../../../../../../ulearn5.js/ulearn5/js/components/ngDialog/css/ngDialog-theme-plain.css',
                '../../../../../../ulearn5.js/ulearn5/js/components/sweetalert/lib/sweet-alert.css',
                '../../../../../../ulearn5.js/ulearn5/js/components/v-modal/dist/v-modal.css',
                '../../portlets/importantnews/importantnews.css',
                '../../portlets/flashesinformativos/flashesinformativos.css',
                '../../portlets/mysubjects/mysubjects.css',
                'css/ulearn/ulearn.css'],
                dest: 'css/ulearn/ulearn-compiled.css',
            },
        },
        cssmin: {
            target : {
				src : ["css/ulearn/ulearn-compiled.css"],
				dest : "css/ulearn-compiled.min.css"
			}
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
                tasks: ['compass:homeupc', 'concat:dist']
            },
            ulearn: {
                files: [
                    'stylesheets/ulearn/*.scss',
                    'stylesheets/ulearn.scss'
                ],
                tasks: ['compass:ulearn', 'concat:ulearn', 'cssmin']
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

    // CWD to theme folder
    grunt.file.setBase('./src/ulearn5/theme/theme/assets');

    grunt.registerTask('default', ["browserSync:plone", "watch"]);
    grunt.registerTask('bsync', ["browserSync:html", "watch"]);
    grunt.registerTask('plone-bsync', ["browserSync:plone", "watch"]);
};
