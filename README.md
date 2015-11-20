# capnconfig
Type-Safe Program Configuration with Cap'n Proto and JSON

When writing programs, especially in compiled languages like C++, it is desirable to be able to configure the program using a config file. A popular approach is to structure the configuration file as a JSON object. However, users of the config file cannot infer from the JSON object the set of valid configuration options. For writers of the program, using JSON means that access to the configuration object is not type safe.
In this project, the idea is to still use a JSON object in the configfile (easy for humans to parse, even without additional helper tools), but to use Cap'n Proto to manipulate the configfile, as well as for accessing the configuration data from within the program, based on a Cap'n Proto schema. 

This tool includes a pythondialog-based (and type-safe) object editor for Cap'n Proto schemas (it looks similar to, for example, the Linux kernel's menuconfig)

### Example

```capnp
struct Configuration
{
  runMode   @0 : Mode;
  verbose   @1 : Bool;
  docs      @4 : List(Int32);

  server : group {
    ip      @2 :Text = "127.0.0.1";
    port    @3 :UInt16 = 10000;
  }

  enum Mode {
    foo @0;
    bar @1;
  }
}
```

![alt text](https://raw.githubusercontent.com/niekbouman/capnconfig/master/docs/capnconfig.png "Screenshot")

