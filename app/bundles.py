from flask_assets import Bundle


css = Bundle(
    'css/bootstrap.min.css',
    'css/vendors/bootstrap-treeview.min.css',
    'css/bootstrap-table.min.css',
    'http://fonts.googleapis.com/css?family=Open+Sans:400,300,600,700',
    'css/vendors/dropzone/dropzone.css',
    'css/vendors/dropzone/base.css',
    'css/demo.min.css',
    'css/dashboard.css',
    'css/styles.css'
)

js = Bundle(
    'js/jquery.min.js',
    'js/resizer.js',
    'js/jquery-ui.min.js',
    'js/jquery.slimscroll.min.js',
    'js/jquery.inputmask.min.js',
    'js/switchery.min.js',
    'js/bootstrap.min.js',
    'js/vendors/bootstrap-treeview.min.js',
    'js/bootstrap-table.min.js',
    'js/bootstrap-table-pt-BR.js',
    'js/bootstrap-table-reorder-columns.js',
    'js/vendors/FileSaver/FileSaver.min.js',
    'js/vendors/js-xlsx/xlsx.core.min.js',
    'js/vendors/jsPDF/jspdf.min.js',
    'js/vendors/jsPDF-AutoTable/jspdf.plugin.autotable.js',
    'js/vendors/bootstrap-table/bootstrap-table-export.js',
    'js/vendors/bootstrap-table/tableExport.min.js',
    'js/jquery.dragtable.js',
    'js/notify.js',
    'js/ultra.js',
    'js/demo.js',
    'js/vendors/dropzone/dropzone.js',
    'js/init.js',
    'js/scripts.js',
    filters='jsmin',
    output='gen/packed.js'
)
