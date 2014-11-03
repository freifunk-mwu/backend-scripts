<!DOCTYPE HTML>
<html>
<head>
    <meta charset="UTF-8" />
    <title>ffmwu ${hostname} ${sub}</title>
    <link href="${prfx}static/favicon.ico" rel="shortcut icon" />
    <link href="${prfx}static/style.css" rel="stylesheet" type="text/css" media="screen" />
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
        <h1>ffmwu <a href="${prfx}index.html">${hostname}</a> ${sub}</h1>
    </header>

    ${content}

    <footer>
        <div>last &mdash; ${timestamp}</div>
    </footer>
</body>
</html>
