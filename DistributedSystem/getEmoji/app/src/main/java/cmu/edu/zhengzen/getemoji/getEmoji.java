/**
 * author: Zheng Zeng
 * email: zhengzen@andrew.cmu.edu
 * This is the model that connects to a web service and pass the input from/to the web service
 */
package cmu.edu.zhengzen.getemoji;

import android.app.Activity;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Build;
import androidx.annotation.RequiresApi;
import com.google.gson.Gson;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.MalformedURLException;

import java.net.URL;
import java.net.URLConnection;

import javax.net.ssl.HttpsURLConnection;

/** Email: zhengzen@andrew.cmu.edu Author: Zheng Zeng */
public class getEmoji {
  //the link to retrieve emoji
  //task 1 url:"https://stormy-everglades-45566.herokuapp.com/?keyword="
  //task 2 url is used here
  final String basic_url = "https://limitless-sands-42327.herokuapp.com/?keyword=";
  GithubEmoji ge = null;
  Bitmap picture;
  Gson gson;
  String keyword;
  //the model to get emoji
//the method to start searching and response to UI
  public void search(String searchTerm, Activity activity, GithubEmoji githubEmoji) {
    this.ge = githubEmoji;
    this.keyword= searchTerm;
    gson = new Gson();
    new BackgroundTask(activity).execute();
  }

//put the task into background
  private class BackgroundTask {

    private Activity activity; // The UI thread

    public BackgroundTask(Activity activity) {
      this.activity = activity;
    }

    private void startBackground() {
      new Thread(new Runnable() {
        public void run() {

          try {
            doInBackground();
          } catch (IOException e) {
            e.printStackTrace();
          } catch (InterruptedException e) {
            e.printStackTrace();
          }
          // This is magic: activity should be set to MainActivity.this
          //    then this method uses the UI thread
          activity.runOnUiThread(new Runnable() {
            public void run() {
              onPostExecute();
            }
          });
        }
      }).start();
    }

    private void execute() {
      // There could be more setup here, which is why
      //    startBackground is not called directly
      startBackground();
    }

    // doInBackground( ) implements whatever you need to do on
    //    the background thread.
    // Implement this method to suit your needs
    private void doInBackground() throws IOException, InterruptedException {
      picture = retrieveEmoji();
    }

    // onPostExecute( ) will run on the UI thread after the background
    //    thread completes.
    // Implement this method to suit your needs
    public void onPostExecute() {
      ge.getEmojiReady(picture);

    }

  }
  /*
   * build the request url, get the image url from the json file returned,
   * and then create the bitmap picture
   * later the picture can be used by the UI thread to do its work.
   */


  private Bitmap retrieveEmoji() throws IOException, InterruptedException {
    String get_emoji_url = basic_url+keyword;
    return setEmojiImage(getImageUrl(get_emoji_url));
  }

  /*
   * Given a url that will return a JSON string
   */
  private String getImageUrl(String url) {
    String result="";
    try {
      URL request_url = new URL(url);
      HttpsURLConnection connection = (HttpsURLConnection) request_url.openConnection();
      connection.setRequestMethod("GET");
      InputStream inputStream = new BufferedInputStream(connection.getInputStream());
      BufferedReader br = new BufferedReader(new InputStreamReader(inputStream));
      String line;
      while ((line = br.readLine())!=null){
        result+=line;
      }
      System.out.println("result:"+ result);
      Emoji image = gson.fromJson(result,Emoji.class);
      return (String) image.getImage_url();
    } catch (Exception e) {
      e.getMessage();
      e.getStackTrace();
      System.out.print("an error happened!");
      return "cmu/edu/zhengzen/getemoji/404notfound.png";
    }
  }
  /*
   * Given a URL referring to an image, return a bitmap of that image
   */
  @RequiresApi(api = Build.VERSION_CODES.P)
  private Bitmap setEmojiImage(final String url) throws MalformedURLException {
    URL image_url = new URL(url);
    try {
      final URLConnection conn = image_url.openConnection();
      conn.connect();
      BufferedInputStream bis = new BufferedInputStream(conn.getInputStream());
      Bitmap bm = BitmapFactory.decodeStream(bis);
      //set the size of the map to fit the screen and for better user view
      bm  = Bitmap.createScaledBitmap(bm,500,500,true);
      return bm;
    } catch (IOException e) {
      e.printStackTrace();
      return null;
    }
  }
}


