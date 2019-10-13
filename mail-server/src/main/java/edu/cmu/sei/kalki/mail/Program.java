package edu.cmu.sei.kalki.mail;

public class Program {

    public static void main(String[] args)
    {
        MailServer.initialize();
        MailServer.registerObserver(new NewMailHandler());

        System.out.println("Waiting for emails.");
        while(true) {
            try
            {
                Thread.sleep(1000);
            } catch (InterruptedException e)
            {
                e.printStackTrace();
            }
        }
    }
}
