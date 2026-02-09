
from flask import Flask, Response

app = Flask(__name__)

@app.route('/vast')
def vast():
    vast_xml = """
<VAST version="4.0">
  <Ad id="sample">
    <InLine>
      <AdSystem>FASTPOC</AdSystem>
      <AdTitle>Sample Test Ad</AdTitle>
      <Creatives>
        <Creative id="cr1" sequence="1">
          <Linear>
            <Duration>00:00:30</Duration>
            <TrackingEvents>
              <Tracking event="start">https://tracker.example.com/start</Tracking>
              <Tracking event="firstQuartile">https://tracker.example.com/q1</Tracking>
              <Tracking event="midpoint">https://tracker.example.com/mid</Tracking>
              <Tracking event="thirdQuartile">https://tracker.example.com/q3</Tracking>
              <Tracking event="complete">https://tracker.example.com/complete</Tracking>
            </TrackingEvents>
            <VideoClicks>
              <ClickThrough><![CDATA[https://example.com/clickthrough]]></ClickThrough>
            </VideoClicks>
            <MediaFiles>
              <MediaFile delivery="progressive" type="video/mp4" bitrate="1500" width="1280" height="720">https://cdn.example.com/ads/sample30.mp4</MediaFile>
            </MediaFiles>
          </Linear>
        </Creative>
        <Creative id="cr2" sequence="2">
          <Linear>
            <Duration>00:00:15</Duration>
            <MediaFiles>
              <MediaFile delivery="progressive" type="video/mp4" bitrate="800" width="854" height="480">https://cdn.example.com/ads/sample15.mp4</MediaFile>
            </MediaFiles>
          </Linear>
        </Creative>
      </Creatives>
      <Impression><![CDATA[https://tracker.example.com/impression]]></Impression>
    </InLine>
  </Ad>
</VAST>
"""
    return Response(vast_xml.strip(), mimetype='text/xml')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)
