@0x904ef3a4494e5e7c;

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

