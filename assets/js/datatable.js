$(document).ready(function () {
    var awesome_list = 'awesome-ios'

    // Build DataTable instance with custom attributes
    var table = $('#curated').DataTable( {
        "ajax" : "data/" + awesome_list + "/__all__.json",
        "columns" : [
            { "data" : "Repo"},
            { "data" : "Description"},
            { "data" : "Stars"},
            { "data" : "Forks"},
            { "data" : "Language"}
        ],

        "paging": true,
        "autoWidth": true,
        "lengthMenu": [ 50, 100, 200, 500 ],
        pageLength: 50,
        "columnDefs": [
            // Repo, Description, Language: Alphabetical A-Z
            { "orderSequence": [ "asc" , "desc" ], "targets": [ 0, 1, 4 ] },
            // Stars, Forks: Numerical High-Low
            { "orderSequence": [ "desc", "asc" ], "targets": [ 2, 3 ] }
            //{ width: '20%', 'targets': [0, 2, 3, 4] },
            //{ width: '60%', 'targets': [1] },
        ],
        responsive: true

    });

    // Load whichever table is selected from the dropdown
    $('.selectpicker').change(function () {
        var selectedItem = $(this).find("option:selected").val();
        file_name = $(this).find("option:selected").attr("id");
        table.ajax.url( 'data/awesome-ios/' + file_name ).load();
    });
});
