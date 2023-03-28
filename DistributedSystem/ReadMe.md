# Creat an Android App To Get Emojis! \smile with Java, Servlet and JSP!

We try to display an emoji on the app as the user instructs us to do. First we need to have an emoji class for best practice.

```{java}
package getemoji;

/**
 * This is the class that store information about an emoji that needs to be sent to the client
 * no additional info rather than the image url needs to be sent.
 **/
public class Emoji {
    //the url of the emoji image, ends in .png
    String image_url;

    //constructor
    public Emoji(String url){
        setImage_url(url);
    }
    //setter and getter
    public void setImage_url(String image_url) {
        this.image_url = image_url;
    }

    public String getImage_url() {
        return image_url;
    }
}
```

## Step 2: write a class to get emoji from GitHub emoji libraries and store it into an emoji object.

```{java}
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

```

## Step 3: write Android App activities to read the image data

```{java}
public class GithubEmoji extends AppCompatActivity {
    GithubEmoji me  = this;
//create function : connect layout to activity


        @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
            /*
             * The click listener will need a reference to this object, so that upon successfully finding an emoji from Github, it
             * can callback to this object with the resulting picture Bitmap.  The "this" of the OnClick will be the OnClickListener, not
             * this GithubEmoji.
             */
        final GithubEmoji ma = this;
        Button submit = (Button)findViewById(R.id.button);
/**
 * activity handler
 * when the user presses submit button, the listener will pass on the input and start connecting to
 * the web service
 */
        submit.setOnClickListener(new View.OnClickListener(){
            public void onClick(View viewParam) {
                //obtain the key word
                String keyWord = ((EditText)findViewById(R.id.keyword)).getText().toString();
                System.out.println("key word for emoji = " + keyWord);
                //the model for connecting to the web service
                getEmoji getEmoji = new getEmoji();
                //start searching
                getEmoji.search(keyWord, me, ma); // Done asynchronously in another thread.  It calls ip.pictureReady() in this thread when complete.
            }
        });
    }

    //make the menu shown
    //not one of the primary methods to be used
    //generated by the template
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    /**
     * the method to show the emoji on the screen
     * @param picture
     */

    public void getEmojiReady(Bitmap picture) {
        //set the view widgets
        ImageView imageView = (ImageView)findViewById(R.id.EmojiImage);
        TextView searchView = (EditText)findViewById(R.id.keyword);
        TextView feedback = (TextView) findViewById(R.id.example);
        feedback.setVisibility(View.INVISIBLE);
        //when the picture is not null
        if (picture != null) {
            imageView.setImageBitmap(picture);
            System.out.println("picture");
            imageView.setVisibility(View.VISIBLE);
            //indicate the result
            feedback.setText("Here is your emoji of "+ ((EditText)findViewById(R.id.keyword)).getText().toString());
            feedback.setVisibility(View.VISIBLE);
        } else {
            //when the image is null
            //show an image that indicates not found
            imageView.setImageResource(R.mipmap.ic_launcher);
            System.out.println("No picture");
            imageView.setVisibility(View.VISIBLE);
            feedback.setText("Sorry, I cannot find a emoji of "+ ((EditText)findViewById(R.id.keyword)).getText().toString());
            feedback.setVisibility(View.VISIBLE);
        }
        searchView.setText("");
        imageView.invalidate();
    }
}
```

## Step 3: Use a servlet to connect to send web requests to show the emoji image.

```{java}
@WebServlet(
    name = "getEmojiServlet",
    urlPatterns = {"/getAnEmoji"})
public class getEmojiServlet extends HttpServlet {
  private getEmoji emoji; // the model of getting the emoji

  public void init() {
    // initiate the getEmoji() object
    try {
      emoji = new getEmoji();
    } catch (IOException e) {
      // catch any exception
      // handling any java side problem
      e.printStackTrace();
    } catch (InterruptedException e) {
      e.printStackTrace();
    }
  }

  /**
   * the doGet method to deal with request and send a json file string to the writer
   *
   * @param request
   * @param response
   * @throws IOException
   */
  public void doGet(HttpServletRequest request, HttpServletResponse response)
      throws IOException, ServletException {
    response.setContentType("text/html");
    String keyword = request.getParameter("keyword");
    // check if the key word is correct
    // acquire the json string from emoji object
    String emoji_image = emoji.getEmojiIcon(keyword);
    // set up the response
    response.setContentType("application/json");
    // write the answer to response
    response.getWriter().write(emoji_image);
  }

  public void destroy() {}
}
```

## Deployment: learn how to deploy an Android App with Intellij.




