try:
    import yt_dlp
    print("yt_dlp_ok:" + yt_dlp.version.__version__)
except ImportError:
    print("no_yt_dlp")
try:
    import requests
    print("requests_ok")
except ImportError:
    print("no_requests")
