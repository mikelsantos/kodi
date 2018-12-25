// TODO: check if file already exists, in such case file will never download and get past 0%

var fs = require('fs')
var http = require('http')
var httprequest = require('httpreq')
var querystring = require('querystring')
var mime = require('mime')
var parseTorrent = require('parse-torrent')
var path = require('path')
var pump = require('pump')
var rangeParser = require('range-parser')
var torrentStream = require('torrent-stream')
var url = require('url')

var PORT = 8080;
var HOST = 'localhost';
var TEMP = null;
var MOVE = null;

var currentFile = null;
var engine = null;

function getFileSize(file){
    fileSize = 0    
    fileStats = null
    fileName = getFileName(file)
    if (fs.existsSync(fileName))
        fileStats = fs.statSync(fileName)
        if (fileStats != null && 'size' in fileStats)
            fileSize = fileStats['size']
    return fileSize
}

function getFileName(file){
    fileName = ''
    if (engine != null && file != null){        
        fileName = engine.path + '\\'  + file.path        
    }
    return fileName
}

function closeStream(stream){
    message = ''
    if (stream != null){
        message = 'ERROR'
        stream.close()        
        message = 'OK'
    }
    return message
}

function stopFile(file){
    message = ''
    if (file != null){
        message = 'ERROR'
        try{
            file.deselect()
            engine.swarm.pause()
            message = 'OK'
        } catch(ex) {}
    }
    return message
}

function copyFile(file, dstDir){
    if (!fs.existsSync(dstDir))
        fs.mkdirSync(dstDir);
    
    var dstFile = dstDir + file.name;
    var is = file.createReadStream();    
    var os = fs.createWriteStream(dstFile);
    is.pipe(os);
    is.on('end', function() {
        console.log('File moved to ' + dstFile);
    });
}

function delFile(file){
    message = ''
    stopFile(file)
    if (engine != null && file != null){
        message = 'ERROR'
        fileName = getFileName(file)
        if (fs.existsSync(fileName)){
            console.log('Deleting ' + fileName)
            fs.unlinkSync(fileName)
        }
        message = 'OK'
    }
    return message
}

function delFiles(){
    if (engine != null){
        for (var i=0;i<engine.files.length;i++)
            delFile(engine.files[i])
        
        engine.remove(false, function (err){
            if (err) console.log(err);
        });
    }
}

function getStreamInfo(){
    var swarmStats = null
    if (engine != null){
        var totalPeers = engine.swarm.wires
        var activePeers = totalPeers.filter(function (wire) {
            return !wire.peerChoking
        })

        var totalLength = engine.files.reduce(function (prevFileLength, currFile) {
            return prevFileLength + currFile.length
        }, 0)

        var toEntry = function (file, i) {
            return {
            name: file.name.toString('utf8'),
            url: 'http://' + HOST + '/' + i,
            path: getFileName(file),
            downloaded: file.downloaded(),
            length: file.length,
            ready: file==currentFile
            }
        }

        swarmStats = {
            totalLength: totalLength,
            downloaded: engine.swarm.downloaded,
            uploaded: engine.swarm.uploaded,
            downloadSpeed: parseInt(engine.swarm.downloadSpeed(), 10),
            uploadSpeed: parseInt(engine.swarm.uploadSpeed(), 10),
            totalPeers: totalPeers.length,
            activePeers: activePeers.length,
            files: engine.files.filter(function () {return true}).map(toEntry)
        }
    }
    return swarmStats
}

function destroyEngine(){
    if (engine != null){
        delFiles();
        engine.destroy(null);
        engine = null;
    }
}

function onDestroy(){
    process.exit();
}

function onTorrentReady(torrent, callback){
    currentFile = null;
    
    if (TEMP == null){
        var os = require('os');
        TEMP = os.tmpdir();
    }
    
    console.log('TEMP: ' + TEMP + ' HOST: ' + HOST + ' PORT: ' + PORT);
    
    opts = {tmp:TEMP, hostname:HOST, port:PORT};   
    
    if (engine) destroyEngine();
     
    engine = torrentStream(torrent, opts, callback);
            
    // TODO: decide whether to remove this part and do nothing until play requested
    engine.on('ready', function () {
        var maxSize = 0;        
        engine.files.forEach(function(file) {            
            console.log('File: %s\\%s [%d]', engine.path, file.path, file.length);            
            if (file.length > maxSize){ 
                maxSize = file.length;                
                currentFile = file;                
            }
        });
        if (engine.files.length == 1) currentFile.select();        
    });
    
    engine.on('uninterested', function () {
        engine.swarm.pause()
    });

    engine.on('interested', function () {
        engine.swarm.resume()
    });
        
    engine.on('completed', function (){
        if (MOVE != null){
            if (currentFile) copyFile(currentFile, MOVE);
        }
    });        

    engine.server = mainServer;
    engine.listen();

    return engine;
}

function parseTorrentInput(torrent, callback){
    if (torrent.length>7 && torrent.substring(0,7)=='magnet:'){
        console.log('GOT MAGNET: ' + torrent);                    
        callback(parseTorrent(torrent));
    }
    else if (torrent.length>4 && torrent.substring(0,4)=='http'){
        console.log('GOT URI: ' + torrent);
        httprequest.get(torrent, {binary: true}, function (err, res){
            if (!err && res){                
                try{
                    callback(parseTorrent(res.body));
                } catch(ex){}
            }
        });
    } else{
        console.log('GOT FILE: ' + torrent);
        fs.readFile(torrent, function (err, data){
            if (!err && data){
                try{
                    callback(parseTorrent(data));         
                } catch(ex){}
            }
        });
    }
}

function jsonResponse(data, response){
    var json = JSON.stringify(data, null, '  ');
    response.setHeader('Content-Type', 'application/json; charset=utf-8');
    response.setHeader('Content-Length', Buffer.byteLength(json));
    if (json) response.write(json);
}

function handleRequest(request, response){
    var queryUrl = url.parse(request.url, true);    
    console.log(queryUrl.pathname);
    switch(queryUrl.pathname){        
        case '/host':
            if ('name' in queryUrl.query){
                host = querystring.unescape(queryUrl.query.name);
                console.log('Setting host to ' + host + '...');                ;
                HOST = host;
            }
            if ('port' in queryUrl.query){
                port = parseInt(querystring.unescape(queryUrl.query.port));
                if (!isNaN(port)){
                    console.log('Setting port to ' + port + '...');                
                    PORT = port;
                } else{
                    console.log('Provided port is not a number ...');                
                }
            }
            response.end();
            break;
        case '/move':
            if ('move' in queryUrl.query){
                movePath = querystring.unescape(queryUrl.query.move);
                console.log('Setting move directory ' + movePath + '...');
                MOVE = movePath;
            }
            response.end();
            break;
        case '/temp':
            if ('path' in queryUrl.query){
                tempPath = querystring.unescape(queryUrl.query.path);
                console.log('Setting temp directory ' + tempPath + '...');
                TEMP = tempPath;
            }
            response.end();
            break;
        case '/data':
            if ('file' in queryUrl.query){                
                filePath = querystring.unescape(queryUrl.query.file);
                console.log('Parsing torrent ' + filePath + '...');
                parseTorrentInput(filePath, function (torrent){
                    jsonResponse(torrent, response);
                    response.end();
                });                
            }            
            break;
        case '/retr':
            destroyEngine();
            currentFile = null;
            if ('path' in queryUrl.query){
                tempPath = querystring.unescape(queryUrl.query.path);
                console.log('Setting temp directory ' + tempPath + '...');
                TEMP = tempPath;
            }
            if ('move' in queryUrl.query){
                movePath = querystring.unescape(queryUrl.query.move);
                console.log('Setting move directory ' + movePath + '...');
                MOVE = movePath;
            }
            if ('file' in queryUrl.query){                
                filePath = querystring.unescape(queryUrl.query.file);
                console.log('Parsing torrent ' + filePath + '...');
                parseTorrentInput(filePath, function (torrent){
                    engine = onTorrentReady(torrent, function(eng){
                        result = {}
                        result['files'] = [];
                        for (var i=0;i<eng.files.length;i++){                            
                            result['files'].push({index:i, name: eng.files[i].name.toString('utf8'), path: getFileName(eng.files[i]), length: eng.files[i].length});
                        }
                        jsonResponse(result, response);
                        response.end();
                    });
                });                
            }            
            break;        
        case '/info':            
            jsonResponse(getStreamInfo(), response);
            response.end();
            break;
        case '/down':
            if ('index' in queryUrl.query){
                index = querystring.unescape(queryUrl.query.index);
                fileIndex = parseInt(index);
                console.log('Selected item ' + index);                                
                if (!isNaN(fileIndex) && engine != null && fileIndex<engine.files.length){
                    currentFile = engine.files[fileIndex];
                    currentFile.select();
                    response.write(currentFile.name);
                }
            }
            response.end();
            break;
        case '/play':            
            if ('file' in queryUrl.query){
                file = querystring.unescape(queryUrl.query.file);
                fileIndex = parseInt(file);
                console.log('Selected item ' + file);
                if (!isNaN(fileIndex) && engine != null && fileIndex<engine.files.length){
                    currentFile = engine.files[fileIndex];
                    currentFile.select();
                }                
            }
            if (currentFile != null){
                var file = currentFile;
                console.log('Playing ' + file.name);
                console.log('Local file is ' + getFileName(file));
                var range = request.headers.range;
                range = range && rangeParser(file.length, range)[0];                                
                response.setHeader('Accept-Ranges', 'bytes');
                response.setHeader('Content-Type', mime.lookup(file.name));                
                request.connection.setTimeout(3600000);                
                if (!range) {
                    response.setHeader('Content-Length', file.length);
                    if (request.method === 'HEAD') {
                      return response.end();
                    }
                    return pump(file.createReadStream(), response);
                } else {
                    response.statusCode = 206;
                    response.setHeader('Content-Length', range.end - range.start + 1);
                    response.setHeader('Content-Range', 'bytes ' + range.start + '-' + range.end + '/' + file.length);
                    if (request.method === 'HEAD') {
                        return response.end();
                    }
                    pump(file.createReadStream(range), response);
                }
            } else response.end();
            break;
        case '/test':
            if (currentFile != null){
                fileName = getFileName(currentFile);
                fileSize = fs.statSync(fileName)['size'];
                range = range && rangeParser(fileSize, range)[0];
                response.setHeader('Accept-Ranges', 'bytes');
                response.setHeader('Content-Type', mime.lookup(fileName));
                request.connection.setTimeout(3600000);
                if (!range) {
                    response.setHeader('Content-Length', fileSize);
                    if (request.method === 'HEAD') {
                      return response.end();
                    }
                    return pump(fs.createReadStream(fileName), response);
                } else {
                    response.statusCode = 206;
                    response.setHeader('Content-Length', range.end - range.start + 1);
                    response.setHeader('Content-Range', 'bytes ' + range.start + '-' + range.end + '/' + file.length);
                    if (request.method === 'HEAD') {
                        return response.end();
                    }
                    pump(fs.createReadStream(fileName, {start: range.start, end: range.end}), response);
                }
            } else response.end();            
            break;
        case '/stop':                    
            response.end(stopFile(currentFile));
            destroyEngine();
            break;
        case '/dele':            
            response.end(delFile(currentFile));            
            destroyEngine();
            break;
        case '/exit':                        
            response.end(delFile(currentFile));
            destroyEngine();
            break;         
        case '/favicon.ico':
            response.statusCode = 404;
            response.end();
            break;
        default:            
            response.end();
            break;         
    }    
}

var mainServer = http.createServer(handleRequest);
mainServer.listen(PORT, function(){
    console.log("Server listening on: http://%s:%s", HOST, PORT);
});