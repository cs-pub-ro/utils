# Anonimizarea catalogului

Acesta este un ghid pentru anonimizarea catalogului, adică afișarea notelor în mod public, dar fără referințe la numele studenților.
În general, acest lucru este necesar atunci când catalogul este stocat într-un document tip foaie de calcul / spreadsheet (incluzând Google Sheets).

Scopul final este de a face foarte ușor pentru o echipă didactică să aibă:
1. o versiune privată a catalogului cu nume, grupuri și alte informații private și toate notele
1. o versiune publică a catalogului cu informațiile private eliminate, adică numai notele disponibile

Ideea din spatele acestui lucru este de a avea un identificator unic pentru fiecare student.
Identificarea unică a identificatorului pentru fiecare elev este disponibilă doar în versiunea privată a catalogului.
Identificatorul unic face parte din versiunea publică a cărții de note împreună cu notele.
Nicio referire la numele studenților nu este disponibilă public.

## Obținerea identificatorilor unici

Fișierul `unique_ids_10000.txt` din acest director conține `10000` identificatori unici cu `12` caractere fiecare.
Numărul necesar de identificatori poate fi selectat (și amestecat) din acest fișier.

Dacă doriți să generați un set diferit de identificatori unici, puteți să:
* Utilizați site-ul https://pwgen.io/en/.
* Utilizați site-ul https://www.pwdgen.org/.
* Utilizați utilitarul în linie de comandă [pwgen] (https://linux.die.net/man/1/pwgen).
  De exemplu, pentru a genera `150` de identificator de câte 12 caractere, utilizați:

  ```bash
  $ pwgen -0 -1 12 150
  aeShoihaisue
  Kaiphuewaihu
  Poofeezuquai
  IezeiLoophaN
  Ooshoowoosaa
  [...]
  ```

  Utilitarul `pwgen` a fost utilizat pentru a genera fișierul` unique_ids_10000.txt`.

## Crearea catalogului privat

Catalogul privat va stoca informațiile de identificare private: student, e-mail, grup, asistent didactic.
Aceste informații sunt furnizate intern de către universitate pentru fiecare clasă.
Poate fi prin secretariat sau printr-o platformă universitară, cum ar fi [Moodle la UPB] (https://curs.upb.ro/).

Presupunând că avem un catalog privat stocat într-un document de foaie de calcul / spreadsheet, asigurați-vă că există coloane pentru:
* informațiile private de identificare: student, e-mail, grup, asistent
* identificatorul unic
* notele (pe componente, inclusiv formulele)

Completați catalogul privat cu informații private și adăugați formule pentru note.

Adăugați identificatorii unici în coloana corespunzătoare.
Acum catalogul privat conține asocierea între informațiile de identificare private și identificatorul unic.

### Observații legate de asocierea studenților la identificatori

Fiecare cursuri are propria asociere student-la-identificator, astfel încât aceiași identificatori pot fi folosiți pentru cursuri diferite.
Chiar și cursurile cu aceiași studenți (discipline diferite la aceeași serie) pot utiliza aceiași identificatori, condiția fiind să fie amestecați înainte de a face o asociere cu numele studenților, adică înainte de a completa coloana identificatorului unic din catalogul privat.

## Generarea catalogului public

Catalogul public de va fi generat ca o foaie în catalogul privat sau ca document privat.
Apoi, informațiile publice din catalogul privat (identificatori unici și note) vor fi legate în documentul public.

Cea mai ușoară modalitate este de a crea o foaie publică nouă în catalogul privat și de a adăuga formule care completează, pentru fiecare celulă a foii publice, conținutul foii private.

## Demonstrație folosind Google Sheets

[Aici](https://docs.google.com/spreadsheets/d/1QOO3HbTEJY70U3IjPkEpw3G_U8TCBfX5RIx6RJkf2zI/edit?usp=sharing) este o demonstrație a utilizării Google Sheets pentru stocarea unui catalog privat / public.
Există 10 foi, 5 private și 5 publice.
Fiecare foaie publică folosește formule pentru a completa celulele cu informațiile publice din foaia privată corespunzătoare: identificator unic și note.
În plus, foile publice sunt protejate pentru a preveni modificările accidentale;
toate actualizările ar trebui să se întâmple numai în foile private.

Utilizând `File -> Sharing -> Publish to the web` în documentul Google, publicăm fiecare foaie publică (toate cele 5 foi).
Astfel, catalogul public este disponibil [aici](https://docs.google.com/spreadsheets/d/e/2PACX-1vRxo6bv-PerDoeGJzRwAAmZdbjlISUf3qZQ52waqyq5dx5csYosnu3S9peS5q9BWP5oiT9Iz).
Rețineți că linkul pentru fiecare foaie are un sufix `?gid=...&single=true`;
eliminați acest sufix și toate foile publice sunt disponibile la același link, ca taburi separate.

### Îmbunătățirea anonimatului

Pentru a îmbunătăți anonimatul, sortați intrările din foile publice după identificator.
Acest lucru va elimina posibilitatea studenților de a-și deduce numele după locul lor în catalogul / registrul de studenți al seriei.

Sortarea intrărilor se face selectând intervalul (*range*) din documentul foii de calcul și sortând-o după coloana identificatorului unic (*Sort range*) .

## Trimiterea identificatorilor unici către studenți

Studenții trebuie să primească în mod privat identificatorii lor unici.

Recomandăm să utilizați [setul de scripturi Python](https://github.com/systems-cs-pub-ro/utils/tree/master/send-email) pentru asta.
Veți crea un fișier CSV cu patru coloane: `firstname`, `lastname`, `email`, `identifier`.
Compuneți un șablon (*template*) de mesaj și utilizați construcția `$identifier` pentru a înlocui în mesajul trimis identificator pentru fiecare student.

Utilizați exemplul de mesaj din fișierul `message.txt` din acest director.
