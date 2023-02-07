---
hide:
  - navigation
  - toc
---
<script>
    var opts = {
        scrollYOffset: 120,
        hideHostname: true,
        hideDownloadButton: true,
        hideSingleRequestSampleTab: true,
        theme: {
            colors: {
                primary: {
                    main: "#333333"
                }
            },
            sidebar: {
                width: "345px",
                backgroundColor: "#FFFFFF",
                textColor: "#424242"
            },
            rightPanel: {
                backgroundColor: "#00284c"
            },
            typography: {
                headings: {
                    fontFamily: "'proxima-nova', sans-serif",
                    fontWeight: 700
                }
            },
            schema: {
                arrow: {
                size: '1.4em',
                color: '#1d8127'
                }
            }
        }
    };
    Redoc.init("https://raw.githubusercontent.com/code42/developer.code42.com/gh-pages/api/code42api.json", opts, document.getElementById("redoc-container"))
</script>
