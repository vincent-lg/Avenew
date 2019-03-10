const STRUCTURE = {
    en: {
        unknown: 'Unknown',
        info: 'info',
        author: 'author',
        ident: 'ident',
        note: 'note',
        room: 'room',
        coords: 'coords',
        title: 'title',
        description: 'description',
        exits: 'exits',
        direciotn: 'direction',
        destination: 'destination',
        name: 'name',
        aliases: 'aliases',
    },
    fr: {
        unknown: 'Inconnu',
        info: 'info',
        author: 'auteur',
        ident: 'ident',
        note: 'note',
        room: 'salle',
        coords: 'coords',
        title: 'titre',
        description: 'description',
        exits: 'sorties',
        direciotn: 'direction',
        destination: 'destination',
        name: 'nom',
        aliases: 'alias',
    },
};
var t = STRUCTURE[lang];
var name = t.unknown;
var author = t.unknown;
var ident = t.unknown;
var note = t.unknown;

$(function() {
    parseDocuments();
    $('#name').text(name);
    $('#author').text(author);
    $('#ident').text(ident);
    $('#note').text(note);
    $('#num-documents').text(documents.length);
});

function parseDocuments() {
    for(var i = 0;i < documents.length;i++) {
        var document = documents[i];
        if(document.type === t.info) {
            name = document[t.name];
            author = document[t.author];
            ident = document[t.ident];
            note = document[t.note];
        }
    }
}
