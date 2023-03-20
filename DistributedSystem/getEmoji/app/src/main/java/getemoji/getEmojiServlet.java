/**
 * author: zhengzen email: zhengzen@andrew.cmu.edu This is the main web service that get a string
 * from the user and return a json file containing the emoji image url
 */
package andrew.cmu.edu.zhengzen.emoji.getemojiservlet;

import jakarta.servlet.RequestDispatcher;
import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import javax.swing.*;
import java.io.IOException;
// set the path name to be getemoji
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
