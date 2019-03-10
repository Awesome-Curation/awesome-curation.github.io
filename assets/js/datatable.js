$(document).ready(function () {
    $('#curated').DataTable( {
        "ajax" : "data/sandbox.json",
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
})

/*
function myFunction() {
    var table = $('#curated').DataTable( {
    } );

    if (document.getElementById("demo-button").style.color == 'red') {
        document.getElementById("demo-button").style.color = "white";
    }
    else {
        table.destroy();
        document.getElementById("demo-button").style.color = "red";
        //table.reload();
    }
}
*/