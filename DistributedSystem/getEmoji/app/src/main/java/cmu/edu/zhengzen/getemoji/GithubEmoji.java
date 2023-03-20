/**
 * author: Zheng Zeng
 * email: zhengzen@andrew.cmu.edu
 * This is the model that handles activities of an application
 */
package cmu.edu.zhengzen.getemoji;

import android.app.Activity;
import android.graphics.Bitmap;
import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;

import android.view.View;

import android.view.Menu;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;


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