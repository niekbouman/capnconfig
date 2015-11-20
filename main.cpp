//usr/bin/clang++ -lcapnp -lkj -std=c++11 "$0" configfile.capnp.c++ && ./a.out; exit
#include <vector>
#include <algorithm>
#include <iostream>
#include "configfile.capnp.h"
#include <capnp/message.h>
#include <capnp/dynamic.h>
#include <capnp/schema.h>
#include "json.hpp"
#include <fstream>
#include <string>


using json = nlohmann::json;

template <typename FieldType>
json& descentScopeIfGroup(json& ref, FieldType field)
{
    json& newRef = ref;

    if(field.getProto().isGroup()){
      std::string groupName = field.getProto().getName().cStr();
      newRef = ref[groupName];
    }

    return newRef;
}

void parseField(::capnp::StructSchema::Field field, json &source,
                ::capnp::DynamicStruct::Builder target) {

  using namespace capnp;



/*
    json* sourceptr = &_source;
    ::capnp::DynamicStruct::Builder target = _target;

    if(field.getProto().isGroup()){
      std::string groupName = field.getProto().getName().cStr();
      sourceptr = &(_source[groupName]);
      target =  _target.init(field).as<DynamicStruct>();
//      std::tie(objPtr, newStruct) = descentScopes(field, obj, capnpStruct);
    }

    json& source = *sourceptr;
*/


  auto fieldName = field.getProto().getName();
  switch (field.getType().which()) {

  case schema::Type::BOOL:
    target.set(field, source[fieldName].get<bool>());
    break;

  case schema::Type::UINT16:
    target.set(field, source[fieldName].get<int>());
 //   target.set(field, source[fieldName].get<std::string>().c_str());
    break;

  case schema::Type::TEXT:
  case schema::Type::ENUM:
    target.set(field, source[fieldName].get<std::string>().c_str());
    break;

  case schema::Type::STRUCT:
  {
    
    std::string groupName = field.getProto().getName().cStr();

    std::cout << "structname " << groupName << std::endl;


    //json* sourceptr = &_source;
    //::capnp::DynamicStruct::Builder target = _target;

    //if(field.getProto().isGroup()){
      //std::string groupName = field.getProto().getName().cStr();
    json& nestedSource = source[groupName];
    auto  nestedTarget = target.init(field).as<DynamicStruct>();


 //     target =  _target.init(field).as<DynamicStruct>();
//      std::tie(objPtr, newStruct) = descentScopes(field, obj, capnpStruct);
   // }

    //json& source = *sourceptr;





    for (auto innerfield:field.getType().asStruct().getFields())
      parseField(innerfield, nestedSource,nestedTarget);

    break;
  }
    
    /*
        for (auto enumerant : field.getType().asEnum().getEnumerants()) {
          std::cout << enumerant.getProto().getName().cStr() << std::endl;
        }
    */
  }
}

/*
std::pair<json *, ::capnp::DynamicStruct::Builder>
descentScopes(::capnp::StructSchema::Field field, json &obj,
              ::capnp::DynamicStruct::Builder capnpStruct) {
  using namespace capnp;
  std::string groupName = field.getProto().getName().cStr();
  return std::make_tuple(&obj[groupName], capnpStruct.init(field).as<DynamicStruct>());
}
*/
void parseObject(json& obj, ::capnp::DynamicStruct::Builder capnpStruct)
{
 using namespace capnp;
 for (auto field: capnpStruct.getSchema().getFields()){
    //auto& nObj = descentScopeIfGroup(obj, field);


    parseField(field,obj,capnpStruct);
  }
}


/*
template <typename FieldType>
void parseField(FieldType field)
{
    auto fieldName = field.getProto().getName();
    using namespace ::capnp;

    switch (field.getType().which()) {

    case schema::Type::BOOL:
      bdyn.set(field, j[fieldName].get<bool>());
      break;

    case schema::Type::ENUM:


      bdyn.set(field, j[fieldName].get<std::string>().c_str());

      for (auto enumerant : field.getType().asEnum().getEnumerants()) {
        cout << enumerant.getProto().getName().cStr() << endl;
      }
      break;
    }


}
*/

int main()
{

  using namespace capnp;
  using namespace std;

  //auto schema = Schema::from<Configuration>(); //.asStruct();

  ifstream is("config.json");

  json j;
  is >> j;
  

  MallocMessageBuilder builder;
  auto b = builder.initRoot<Configuration>();

  DynamicStruct::Builder bdyn = b;

  parseObject(j, bdyn);

  //bdyn.as<
  cout << b.getGridAgent().getIp().cStr() << endl;
  cout << b.getGridAgent().getPort() << endl;
  cout <<( (b.getMode() == Configuration::Mode::BAR) ? "bar" : "foo") << endl;
  cout <<( (b.getVerbose() ) ? "true" : "false") << endl;



  //auto bdyn = b.as<DynamicStruct>();
  
  //DynamicValue::Reader v = b ;

  //v.getType();
  //v.

/*
  for (auto field: bdyn.getSchema().getFields()){

    cout << field.getProto().getName().cStr() << endl;

    cout << int(field.getType().which()) << endl;


    //if (field.getProto().isGroup())
    //  cout << "we're a group!" << endl;

    //field.getProto().getGroup()
    json& jref = j;

    auto fieldName = field.getProto().getName();

    switch (field.getProto().which()) {
    case schema::Field::SLOT:
      cout << "we're a slot" << endl;
      break;
    case schema::Field::GROUP:

      field.getProto().getGroup();
      for (auto nf : field.getType().asStruct().getFields())
        cout << nf.getProto().getName().cStr() << endl;

      cout << "we're a group!" << endl;

      std::string mys = field.getProto().getName().cStr();
      jref = j[mys];
      break;
    }

    switch (field.getType().which()) {

    case schema::Type::BOOL:
      bdyn.set(field, j[fieldName].get<bool>());
      break;

    case schema::Type::ENUM:


      bdyn.set(field, j[fieldName].get<std::string>().c_str());

      for (auto enumerant : field.getType().asEnum().getEnumerants()) {
        cout << enumerant.getProto().getName().cStr() << endl;
      }
      break;
    }

    //case schema::Field::GROUP

 //   case schema::Type::STRUCT
    //field.getType().isText

//getName().cStr() << endl;


  }

*/

 // auto b = builder.initRoot<DynamicStruct>();
 
  vector<int> v = {1,2,3,4};

  for_each(v.begin(), v.end()-1, [](const int& x) { cout << x << endl;});


  return 0;
}
