module my_module
  implicit none
contains

  subroutine module_subroutine1()
    print *, "Hello from module_subroutine1 in my_module"
    call internal_helper()
  end subroutine module_subroutine1

  subroutine module_subroutine2()
    print *, "Hello from module_subroutine2 in my_module"
  end subroutine module_subroutine2

  subroutine internal_helper()
    print *, "Hello from internal_helper in my_module"
  end subroutine internal_helper

end module my_module
