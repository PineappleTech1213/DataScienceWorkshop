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
