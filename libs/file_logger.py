# vim:set et ts=4 sw=4:
import logging
class FileLogger(object):
    """
    This becomes a File Like object that can be be written to. But
    instead of actually writing to a file it writes to a logger object

    Example:
    #Redirect stdout and stderr to a logging object
    import sys
    from file_logger import FileLogger
    import logging
    import socket
    logger=logging.handlers.SysLogHandler(address='/dev/log',facility='user',socktype=socket.SOCK_DGRAM)
    sys.stderr.close()
    sys.stdout.close()
    sys.stderr=FileLogger(logger,logging.ERROR)
    sys.stdout=FileLogger(logger,logging.INFO)

    print("This message should now go to INFO logging level to syslog 'user' facility etc..")
    """
    def __init__(self,logger,level=logging.INFO,prepend_all_lines=True):
        """
        Args:
            logger              Logging Handler object to write to
            level               Valid logging level. Default: logging.INFO
            prepend_all_lines   Bool. Whether multiline messages should be
                                treated as individual lines or one message.
        """
        self.logger=logger
        self.level=level
        if prepend_all_lines:
            self.write=self.__write_prepend
        else:
            self.write=lambda m: self.logger.log(self.level,m)
    def __write_prepend(self,message):
        """
        This can replace the "write" function to treat multiline messages as
        individual messages per line.

        Args:
            message     String to be written
        """
        msgs=message.split('\n')
        for m in msgs:
            if m:
                self.logger.log(self.level,m)
    def read(self,**kwargs):
        raise NotImplemented("FileLogger is write only")
    def close(self):
        return
    def flush(self):
        return
