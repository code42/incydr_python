---
hide:
  - navigation
  - toc
---
#
<div id="redoc-container"></div>
<script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
<script>
    var opts = {
        expandResponses: "200",
        hideHostname: true,
        scrollYOffset: 68,
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
    Redoc.init("../code42api.json", opts, document.getElementById("redoc-container"))
</script>
<style>
.md-grid {
    max-width: 100rem;
}
html,body{margin:0}@media print,screen and (max-width: 75rem){h1{margin:-40px 0}}h2{color:#333333 !important}#redoc-container .api-content{margin-top:68px}#redoc-container .api-content a{text-decoration:none;color:#1976d2}#redoc-container .api-content a:hover{color:#1565c0}#redoc-container .menu-content{border-right:1px solid rgba(0,0,0,0.2)}#redoc-container .menu-content ul li{font-size:0.875rem !important;font-weight:400}#redoc-container .menu-content .scrollbar-container>ul>li{font-size:1rem !important;font-weight:700}#redoc-container .menu-content .scrollbar-container>ul+div{display:none}div[data-section-id]{padding:5px 0 !important}
</style>
