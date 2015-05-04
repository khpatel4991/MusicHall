//Page Ready
//TODO: GET Request for 3 sections
var img = document.getElementById("loaderImg");
$(document).ready(function () {
    loadPlaylist(0);
    $.get("/addsong/", function (data) {
        $('#songPanel').html(data);
    });
    $.get("/addartist/", function (data) {
        $('#artistPanel').html(data);
    });
    $.get("/addgenre/", function (data) {
        $('#genrePanel').html(data);
    });
    $.get("/addcountry/", function (data) {
        $('#countryPanel').html(data);
    });

});

function loadPlaylist(doWork)
{
    $('#playlist_place').html(img);
    console.log("get Playlist");
    $.get("/updateplaylist/" + doWork + "/", updatePlaylist);
}

function updatePlaylist(data, textStatus, jqXHR)
{
    $('#playlist_place').html(data);
}

//Filter Songs
$(function () {
    $('#filterSong').keyup(function () {
        if ($('#filterSong').val().length > 2) {
            $("#filteredSongs").html(img);
            $.ajax({
                type: "POST",
                url: "/filtersongs/",
                data: {
                    'search_text': $('#filterSong').val(),
                    'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
                },
                success: searchSuccessSong,
                dataType: 'html'
            });
        }
        else {
            $("#filteredSongs").html("More than 2 chars");
        }
    });
});


function hideSongList() {
    $('#filteredSongs').html('');
}

function searchSuccessSong(data, textStatus, jqXHR) {
    $('#filteredSongs').html(data);
}

//Filter Artists
$(function () {
    $('#filterArtist').keyup(function () {
        if ($('#filterArtist').val().length > 2) {
            $("#filteredArtists").html(img);
            $.ajax({
                type: "POST",
                url: "/filterartists/",
                data: {
                    'search_text': $('#filterArtist').val(),
                    'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
                },
                success: searchSuccessArtist,
                dataType: 'html'
            });
        }
        else {
            $("#filteredArtists").html("More than 2 chars");
        }
    });
});

function hideArtistList() {
    $('#filteredArtists').html('');
}

function searchSuccessArtist(data, textStatus, jqXHR) {
    $('#filteredArtists').html(data);
}

//Filter Genres
$(function () {
    $('#filterGenre').keyup(function () {
        console.log($('#filterGenre').val());
        if ($('#filterGenre').val().length > 2) {
            $("#filteredGenres").html(img);
            $.ajax({
                type: "POST",
                url: "/filtergenres/",
                data: {
                    'search_text': $('#filterGenre').val(),
                    'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
                },
                success: searchSuccessGenre,
                dataType: 'html'
            });
        }
        else {
            $("#filteredGenres").html("More than 2 chars");
        }
    });
});

function hideGenreList() {
    $('#filteredGenres').html('');
}

function searchSuccessGenre(data, textStatus, jqXHR) {
    $('#filteredGenres').html(data);
}

//Filter Country
$(function () {
    $('#filterCountry').keyup(function () {
        console.log($('#filterCountry').val());
        if ($('#filterCountry').val().length > 0) {
            $("#filteredCountries").html(img);
            $.ajax({
                type: "POST",
                url: "/filtercountries/",
                data: {
                    'search_text': $('#filterCountry').val(),
                    'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
                },
                success: searchSuccessCountry,
                dataType: 'html'
            });
        }
    });
});

function hideCountryList() {
    $('#filteredCountries').html('');
}

function searchSuccessCountry(data, textStatus, jqXHR) {
    $('#filteredCountries').html(data);
}

//Add/Remove Song
function addSong(songId) {
     $.ajax({
        type: "POST",
        url: "/addsong/",
        data: {
            'song_to_add': songId,
            'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
        },
        success: updateSongPanel,
        dataType: 'html'
    });
}

function removeSong(songId) {
    $.ajax({
        type: "POST",
        url: "/removesong/",
        data: {
            'song_to_remove': songId,
            'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
        },
        success: updateSongPanel,
        dataType: 'html'
    });
}

function updateSongPanel(data, textStatus, jqXHR) {
    $('#songPanel').html(data);
    loadPlaylist(0);
}

//Add/Remove Artist
function addArtist(artistId)
{
    $.ajax({
            type: "POST",
            url: "/addartist/",
            data: {
                'artist_to_add': artistId,
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
            },
            success: updateArtistPanel,
            dataType: 'html'
    });
}

function removeArtist(artistId) {
    $.ajax({
        type: "POST",
        url: "/removeartist/",
        data: {
            'artist_to_remove': artistId,
            'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
        },
        success: updateArtistPanel,
        dataType: 'html'
    });
}

function updateArtistPanel(data, textStatus, jqXHR)
{
    $('#artistPanel').html(data);
    loadPlaylist(1);
}

//Add/Remove Genre
function addGenre(genre) {
    console.log("in 2 with genre = " + genre);
    $.ajax({
        type: "POST",
        url: "/addgenre/",
        data: {
            'genre_to_add': genre,
            'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
        },
        success: updateGenrePanel,
        dataType: 'html'
    });
}

function removeGenre(genre) {
    $.ajax({
        type: "POST",
        url: "/removegenre/",
        data: {
            'genre_to_remove': genre,
            'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
        },
        success: updateGenrePanel,
        dataType: 'html'
    });
}

function updateGenrePanel(data, textStatus, jqXHR)
{
    $('#genrePanel').html(data);
    loadPlaylist(1);
}

//Add/Remove Country
function addCountry(country) {
    console.log("in with country = " + country);
    $.ajax({
        type: "POST",
        url: "/addcountry/",
        data: {
            'country_to_add': country,
            'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
        },
        success: updateCountryPanel,
        dataType: 'html'
    });
}

function removeCountry(country) {
    $.ajax({
        type: "POST",
        url: "/removecountry/",
        data: {
            'country_to_remove': country,
            'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()
        },
        success: updateCountryPanel,
        dataType: 'html'
    });
}

function updateCountryPanel(data, textStatus, jqXHR) {
    $('#countryPanel').html(data);
    loadPlaylist(1);
}

//Toast Message Timeout
$(function () {
    // setTimeout() function will be fired after page is loaded
    // it will wait for 5 sec. and then will fire
    // $("#successMessage").hide() function

    setTimeout(function () { $('#successMessage').hide(); }, 5000);
});

function youtubeThingy(random)
{
    window.open('/yplayer/'+random+'/');
}