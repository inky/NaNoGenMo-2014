Disgrice
========

My entry for [NaNoGenMo 2014][nanogenmo2014].

`disgrice.py` is a script which attempts to violate [Grice's maxims][grice].
It applies simple, silly transformations to a text, lending the text a voice
that is familiar but hopelessly unreliable, even paranoid.


Disgriceful texts
-----------------

  * [Alice's Adventures in Wonderland][alice]
  * [The Adventures of Sherlock Holmes][holmes]


Usage
-----

    $ export WORDNIK_API_KEY="yourAPIkey"
    $ python disgrice.py < input.txt > output.html

To use this script you will need the following:

  * A [Wordnik API][wordnik_api] key.
  * Two Python libraries: [pattern][pattern] and [requests][requests].


<hr>

([NaNoGenMo thread](https://github.com/dariusk/NaNoGenMo-2014/issues/33))

[alice]: http://solus.fm/2014/nanogenmo/alice.html
[holmes]: http://solus.fm/2014/nanogenmo/holmes.html

[grice]: http://www.sas.upenn.edu/~haroldfs/dravling/grice.html
[nanogenmo2014]: https://github.com/dariusk/NaNoGenMo-2014
[pattern]: http://www.clips.ua.ac.be/pages/pattern
[requests]: http://docs.python-requests.org/en/latest/
[wordnik_api]: http://developer.wordnik.com/
