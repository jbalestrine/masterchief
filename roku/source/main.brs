' MasterChief DevOps - WebView RSG channel
sub Main(args as Dynamic)
    screen = CreateObject("roSGScreen")
    port = CreateObject("roMessagePort")
    screen.setMessagePort(port)
    scene = screen.CreateScene("MainScene")
    screen.show()

    ' Set the URL after scene is shown
    wv = scene.findNode("webView")
    if wv <> invalid
        wv.setFocus(true)
        wv.uri = "http://ciacpu.myddns.me:8080/"
    end if

    while true
        msg = wait(0, port)
        if type(msg) = "roSGScreenEvent"
            if msg.isScreenClosed() then return
        end if
    end while
end sub
