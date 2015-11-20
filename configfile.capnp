@0x904ef3a4494e5e7c;

struct Configuration
{
  mode    @0 : Mode;
  verbose @1 : Bool;

  li      @7 : List(Int32);
  enum Mode {
    foo @0;
    bar @1;
    coo @2;
  }

  gridAgent : group {
    ip @2 :Text = "127.0.0.1";
    port @3 :UInt16;
  }

  test @4 :Tux;

  union {
    myvoid  @5 :Void;
    bla     @6 :Int16;
  }


}

struct Tux {
  name @0 :Text;
}


