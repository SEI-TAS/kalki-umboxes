package edu.cmu.sei.ttg.kalki.dni;

/**
 * Entry point for the program.
 */

public class Program
{
    /**
     * Entry point for the program.
     */
    public static void main(String[] args)
    {
        try
        {
            DNISetup.startUpComponents();
        }
        catch(Exception e)
        {
            e.printStackTrace();
        }
    }
}
