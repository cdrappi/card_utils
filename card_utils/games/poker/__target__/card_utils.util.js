'use strict';import{AssertionError,AttributeError,BaseException,DeprecationWarning,Exception,IndexError,IterableError,KeyError,NotImplementedError,RuntimeWarning,StopIteration,UserWarning,ValueError,Warning,__JsIterator__,__PyIterator__,__Terminal__,__add__,__and__,__call__,__class__,__envir__,__eq__,__floordiv__,__ge__,__get__,__getcm__,__getitem__,__getslice__,__getsm__,__gt__,__i__,__iadd__,__iand__,__idiv__,__ijsmod__,__ilshift__,__imatmul__,__imod__,__imul__,__in__,__init__,__ior__,__ipow__,
__irshift__,__isub__,__ixor__,__jsUsePyNext__,__jsmod__,__k__,__kwargtrans__,__le__,__lshift__,__lt__,__matmul__,__mergefields__,__mergekwargtrans__,__mod__,__mul__,__ne__,__neg__,__nest__,__or__,__pow__,__pragma__,__proxy__,__pyUseJsNext__,__rshift__,__setitem__,__setproperty__,__setslice__,__sort__,__specialattrib__,__sub__,__super__,__t__,__terminal__,__truediv__,__withblock__,__xor__,abs,all,any,assert,bool,bytearray,bytes,callable,chr,copy,deepcopy,delattr,dict,dir,divmod,enumerate,filter,float,
getattr,hasattr,input,int,isinstance,issubclass,len,list,map,max,min,object,ord,pow,print,property,py_TypeError,py_iter,py_metatype,py_next,py_reversed,py_typeof,range,repr,round,set,setattr,sorted,str,sum,tuple,zip}from"./org.transcrypt.__runtime__.js";import{List,Union}from"./typing.js";var __name__="card_utils.util";export var untuple_dict=function(the_dict){var to_key=function(obj){return isinstance(obj,tuple)?"({})".format(",".join(function(){var __accu0__=[];for(var o of obj)__accu0__.append(str(o));
return py_iter(__accu0__)}())):obj};return function(){var __accu0__=[];for(var [k,v]of the_dict.py_items())__accu0__.append([to_key(k),v]);return dict(__accu0__)}()};export var inverse_cumulative_sum=function(increasing_numbers){if(!increasing_numbers)return[];var inv_cumsum=[increasing_numbers[0]];for(var [e1,e2]of zip(increasing_numbers.__getslice__(0,-1,1),increasing_numbers.__getslice__(1,null,1)))inv_cumsum.append(e2-e1);return inv_cumsum};

//# sourceMappingURL=card_utils.util.map