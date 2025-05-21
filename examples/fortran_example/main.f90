program main
  use my_module
  implicit none

  call module_subroutine1()
  call module_subroutine2()
  call standalone_subroutine()

contains

  subroutine standalone_subroutine()
    print *, "Hello from standalone_subroutine"
  end subroutine standalone_subroutine

end program main
