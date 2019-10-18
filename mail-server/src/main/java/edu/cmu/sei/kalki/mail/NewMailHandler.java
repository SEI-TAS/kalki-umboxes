package edu.cmu.sei.kalki.mail;

public class NewMailHandler implements EventObserver
{
    @Override
    public void notify(String message)
    {
        System.out.println("Message received!: " + message);
    }

}
