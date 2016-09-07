function i4_bit_hi1 ( n )

!*****************************************************************************80
!
!! I4_BIT_HI1 returns the position of the high 1 bit base 2 in an integer.
!
!  Discussion:
!
!    This routine uses the default integer precision, which is
!    presumed to correspond to a KIND of 4.
!
!  Example:
!
!       N    Binary    Hi 1
!    ----    --------  ----
!       0           0     0
!       1           1     1
!       2          10     2
!       3          11     2
!       4         100     3
!       5         101     3
!       6         110     3
!       7         111     3
!       8        1000     4
!       9        1001     4
!      10        1010     4
!      11        1011     4
!      12        1100     4
!      13        1101     4
!      14        1110     4
!      15        1111     4
!      16       10000     5
!      17       10001     5
!    1023  1111111111    10
!    1024 10000000000    11
!    1025 10000000001    11
!
!  Licensing:
!
!    This code is distributed under the GNU LGPL license.
!
!  Modified:
!
!    28 May 2004
!
!  Author:
!
!    John Burkardt
!
!  Parameters:
!
!    Input, integer ( kind = 4 ) N, the integer to be measured.
!    N should be nonnegative.  If N is nonpositive, I4_BIT_HI1
!    will always be 0.
!
!    Output, integer ( kind = 4 ) I4_BIT_HI1, the number of bits base 2.
!
  implicit none

  integer ( kind = 4 ) bit
  integer ( kind = 4 ) i4_bit_hi1
  integer ( kind = 4 ) i
  integer ( kind = 4 ) n

  i = n
  bit = 0

  do

    if ( i <= 0 ) then
      exit
    end if

    bit = bit + 1
    i = i / 2

  end do

  i4_bit_hi1 = bit

  return
end