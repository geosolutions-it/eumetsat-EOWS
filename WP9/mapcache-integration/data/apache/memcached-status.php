<?php
    print nl2br('Memcached - Status' . PHP_EOL);
    print nl2br('--------------------------' . PHP_EOL);
    $out = shell_exec('echo "stats items" | nc 172.17.0.1 11211');
    print nl2br($out) . PHP_EOL;
?>