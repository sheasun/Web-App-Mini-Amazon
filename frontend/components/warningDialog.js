import {Dialog} from '@material-ui/core';

export default function WarningDialog({_open, _close, _onClose, _message}){
  return (
    <Dialog open={_open} onClose={_onClose}>
      <div className='p-2 space-y-2'>
        <div className='text-center py-2'>
          <p className='font-bold'>Error</p>
        </div>
        <div className='flex flex-col justify-top  p-2 space-y-1'>
          <p>{_message}</p>
        </div>
        <div className='text-center'>
          <button className='btn' onClick={_close}>Close</button>
        </div>
      </div>
    </Dialog>
  );
}