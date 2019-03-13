$(document).ready(function () {
    var awesome_list = 'awesome-ios'

    // Build DataTable instance with custom attributes
    var table = $('#curated').DataTable( {
        "columnDefs": [
            { "data" : "Repo",        "targets": 0},
            { "data" : "Description", "targets": 1},
            { "data" : "Stars",       "targets": 2},
            { "data" : "Forks",       "targets": 3},
            { "data" : "Language",    "targets": 4},

            // Repo, Description, Language: Alphabetical A-Z
            { "orderSequence": [ "asc" , "desc" ], "targets": [ 0, 1, 4 ] },

            // Stars, Forks: Numerical High-Low
            { "orderSequence": [ "desc", "asc" ], "targets": [ 2, 3 ] },

            // Can't figure out how to not break col 1 w/o ruining sizing (becomes way too big when 'All' showing)
            { width: '20%', 'targets': [0]},
            { targets:[0, 1], class:"break"}
        ],

        "autoWidth": false,
        "ajax" : "data/" + awesome_list + "/__all__.json",
        "lengthMenu": [ [50, 100, 200, 500, -1], [50, 100, 200, 500, "All"] ],
        "paging": true,
        pageLength: 50,
        responsive: true
    });

    $('#curated td').css('white-space','initial');

    // Load whichever table is selected from the dropdown
    $('.selectpicker').change(function () {
        var selectedItem = $(this).find("option:selected").val();
        file_name = $(this).find("option:selected").attr("id");
        table.ajax.url( 'data/' + awesome_list + '/' + file_name ).load();
        
        table.columns.adjust().draw();
    });
});
