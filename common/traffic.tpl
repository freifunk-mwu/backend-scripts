<!DOCTYPE HTML>
<html>
<head>
    <meta charset="UTF-8" />
    <title>ffmwu ${hostname} traffic</title>
    <link href="favicon.ico" rel="shortcut icon" />
    <style type="text/css">
        body
        {
            background: #ffffff;
            color: #000000;
            font-family: "Source Code Pro", "Consolas", "Courier New", "Monaco", monospace;
            font-size: 12px;
            white-space: nowrap;
        }
        footer
        {
            margin: 2em 0;
        }
        .ifblock
        {
            display: inline-block;
            vertical-align: top;
            text-align: center;
            margin: .1em;
            padding: .5em;
            min-width: 10em;
            border: #cccccc 1px solid;
            border-radius: .5em;
        }
        .ifimg
        {
             display: block;
        }
    </style>
    <script type="text/javascript">
    <!--
        function toggle(id)
        {
            var e = document.getElementById(id);
            e.style.display = (e.style.display == 'none') ? 'block' : 'none';
        }
    -->
    </script>
</head>
<body>
    <header>
        <h1>ffmwu ${hostname} traffic</h1>
    </header>

${traffic}

    <footer>
        <div>ffmwu ${hostname} traffic ${timestamp}</div>
    </footer>
</body>
</html>
