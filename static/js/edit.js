
// add a contributor for the json edit file through js rather than flask backend
let buttonAddContributor = document.getElementById('addContributor')
buttonAddContributor.addEventListener('click', event => {
    console.log("add author"), false;

    let contributorIndexLength = document.getElementById("contributorList").getElementsByClassName("contributors").length;
    console.log('contributorIndex: ' + contributorIndexLength);
    // refer to the html template that contains the contributor input fields
    const tmpl = document.getElementById('contributorTemplate').content.cloneNode(true);
    // tmpl.querySelector('.last').innerText = newContributor.last;
    tmpl.querySelector('.last').setAttribute('name', `last${contributorIndexLength}`);
    tmpl.querySelector('.middle').setAttribute('name', `middle${contributorIndexLength}`);
    tmpl.querySelector('.first').setAttribute('name', `first${contributorIndexLength}`);
    tmpl.querySelector('.affiliation').setAttribute('name', `affiliation${contributorIndexLength}`);
    tmpl.querySelector('.email').setAttribute('name', `email${contributorIndexLength}`);
    tmpl.querySelector('.orcid').setAttribute('name', `orcid${contributorIndexLength}`);
    tmpl.querySelector('.sequence').setAttribute('name', `sequence${contributorIndexLength}`);
    tmpl.querySelector('.bio').setAttribute('name', `bio${contributorIndexLength}`);
    tmpl.querySelector('.bio_fr').setAttribute('name', `bio_fr${contributorIndexLength}`);
    // tmpl.querySelector('.navLinkBioEn').setAttribute('href', `#bio${contributorIndexLength}`);
    // tmpl.querySelector('.navLinkBioFr').setAttribute('href', `#bioFr${contributorIndexLength}`);
    tmpl.querySelector('.bio').setAttribute('id', `bio${contributorIndexLength}`);
    tmpl.querySelector('.bio_fr').setAttribute('id', `bio_fr${contributorIndexLength}`);
    // TODO: add all the elements of the template, names of input fields etc.
    // TODO same for id and label FOR so that it enters field on click (connected by ID!)
    document.getElementById('contributorList').appendChild(tmpl);
})

function createContributorList() {
    let theContributors = []; // the list that will hold the contributors
    // iterate over the contributors
    document.querySelectorAll('.contributors').forEach(function (el) {
        // identify the fields that need to be put into the contributor object
        let theSequence = el.querySelector('.sequence').value;
        let theLast = el.querySelector('.last').value;
        let theMiddle = el.querySelector('.middle').value;
        let theFirst = el.querySelector('.first').value;
        let theEmail = el.querySelector('.email').value;
        let theOrcid = el.querySelector('.orcid').value;
        let theAffiliation = el.querySelector('.affiliation').value;
        let theBioEn = el.querySelector('.bio').value;
        let theBioFr = el.querySelector('.bio_fr').value;
        // create an object from the class names in the html
        let theContributor = {
            sequence: theSequence,
            last: theLast,
            middle: theMiddle,
            first: theFirst,
            email: theEmail,
            orcid: theOrcid,
            affiliation: theAffiliation,
            bio: theBioEn,
            bio_fr: theBioFr
        } // the contributor object

        theContributors.push(theContributor); //add contributor object to contributors list
    });
    return theContributors
}

$('form').on('submit', function (event) {
    let theFile = document.getElementById('fileID').innerText
    console.log(theFile)
    let contributors = JSON.stringify(createContributorList())
    // console.log(contributors)
    // { #put contributors into a div at the top# }
    // { #$('#contributors').html(contributors)# }
    $.ajax({
        data: {
            title: $('#title').val(),
            title_fr: $('#title_fr').val(),
            abstract: $('#abstract').val(),
            abstract_fr: $('#abstract_fr').val(),
            short_title: $('#short_title').val(),
            short_author: $('#short_author').val(),
            keywords: $('#keywords').val(),
            keywords_fr: $('#keywords_fr').val(),
            pages: $('#pages').val(),
            first_page: $('#first_page').val(),
            number_in_issue: $('#number_in_issue').val(),
            doi: $('#doi').val(),
            contributors: contributors
        },
        type: 'POST',
        url: '/edit/' + theFile, // ? '/jedit/'
        success: function (response) {
            console.log('success');
        },
        error: function (error) {
            console.log(error);
        }
    })
        .done(function (data) {
            // { #$('#output').text(data.output).show()# }
            // { #console.log(data)# }
            console.log('function completed')
        });
    event.preventDefault();
});

