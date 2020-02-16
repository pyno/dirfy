# dirfy
an async webpath scanner based on [asyhttp](https://github.com/ax/asyhttp).

## install
To install simply cone the repository and install the requirements.
```bash
$ git clone git@github.com:pyno/dirfy.git
$ cd dirfy
$ pip3 install -r dependencies.txt
```

## usage

Simple usage:
```bash
$ python3 dirfy.py -u http://url.to.test
```
get help:
```bash
$ python3 dirfy.py -h
```

## features
Main features of dirfy:
 - cmdline
 - Asynchronous HTTP(S)
 - Proxy support (-p)
 - Extensions search (-e)
 - Configurable path dictionary (-d)
 - Configurable speed (-c)
 - Configurable redirection behaviour (-r)
 - Support for false positives detection (-f)
 - Request logging (-n to disalbe)
 
## advaced usage
### false positives
Some typicall advanced usages includes the false positives exclusions. Dirfy detects the presence of a page by looking at the HTTP return code: 200 means we found something. Oftentimes, especially when following redirects, this leads to false positives:
```HTTP
HTTP/1.1 200 OK
Content-Length: 57
Content-Type: text/html
Connection: Closed

<html>
  <body>
    Resource not found
  </body>
</hmtml>
```
```HTTP
HTTP/1.1 200 OK
Content-Length: 57
Content-Type: text/html
Connection: Closed

<html>
  <body>
    Please log-in
    ...
  </body>
</hmtml>
```

To exclude such responses from results, just include in the file `false_pos.txt`
```
Resource not found
Please log-in
```
and invoke dirfy as follow:
```bash
$ python3 dirfy.py -u http://url.to.test -f false_pos.txt
```
Note that each line of the file is treated as an indicator of a false positive.

### log
Dirfy logs each request made in a file named log.txt. To disable logging, just run it with `-n` option.
