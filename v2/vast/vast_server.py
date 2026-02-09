from flask import Flask, Response
app = Flask(__name__)

@app.route('/vast')
def vast():
    vast_xml = """
    <VAST version="3.0">
      <Ad id="demo">
        <InLine>
          <Creatives>
            <Creative>
              <Linear>
                <Duration>00:00:30</Duration>
                <MediaFiles>
                  <MediaFile type="video/mp4">
                    https://example.com/ads/sample_ad_30s.mp4
                  </MediaFile>
                </MediaFiles>
              </Linear>
            </Creative>
          </Creatives>
        </InLine>
      </Ad>
    </VAST>
    """
    return Response(vast_xml, mimetype='text/xml')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)
