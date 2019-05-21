package edu.cmu.sei.ttg.kalki.dni.umbox;

import kalkidb.database.Postgres;
import kalkidb.listeners.IInsertHandler;
import kalkidb.models.DeviceSecurityState;
import kalkidb.models.UmboxImage;
import kalkidb.models.UmboxInstance;

import java.util.List;

public class DeviceSecurityStateInsertHandler implements IInsertHandler
{
    @Override
    public void handleNewInsertion(int deviceSecurityStateId)
    {
        // TODO: switch this to get a specific security state change.
        DeviceSecurityState stateChange = Postgres.findDeviceSecurityState(deviceSecurityStateId);
        int deviceId = stateChange.getDeviceId();

        // Find umboxes for given state and device
        // Get umbox image info.
        Postgres.findDevice(deviceId).whenComplete((device, exception) ->
        {
            Postgres.findUmboxInstances(deviceId).whenComplete((umboxInstances, instException) ->
            {
                // First clear the current umboxes.
                for(UmboxInstance instance : umboxInstances)
                {
                    // Image is not really needed for existing umboxes that we just want to stop, thus null.
                    Umbox umbox = new VMUmbox(null, Integer.parseInt(instance.getAlerterId()));
                    DAGManager.clearUmboxForDevice(umbox, device);
                }

                // TODO: better sync this? Maybe first create new umboxes, then clear previous rules,
                //  then redirect and then stop old ones?
                // Now create the new ones.
                List<UmboxImage> umboxImages = Postgres.findUmboxImagesByDeviceTypeAndSecState(device.getType().getId(), stateChange.getId());

                // TODO: add support for multiple umbox images in one DAG.
                UmboxImage image = umboxImages.get(0);
                if(image != null)
                {
                    System.out.println("Starting umbox and setting rules.");
                    DAGManager.setupUmboxForDevice(image, device);
                }
                else
                {
                    System.out.println("No umbox associated to this state.");
                }
            });
        });
    }
}
