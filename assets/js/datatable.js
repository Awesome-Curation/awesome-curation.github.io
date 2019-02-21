$(document).ready(function () {
    $('#curated').DataTable( {
        "paging": true,
        "lengthMenu": [ 50, 100, 200, 500 ],
        pageLength: 50,
        "columnDefs": [
            // Repo, Description, Language: Alphabetical A-Z
            { "orderSequence": [ "asc" , "desc" ], "targets": [ 0, 1, 4 ] },
            // Stars, Forks: Numerical High-Low
            { "orderSequence": [ "desc", "asc" ], "targets": [ 2, 3 ] }
        ],
        responsive: true
    });
})
