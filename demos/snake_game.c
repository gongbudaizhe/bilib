/*
 * snake_game.c
 * Copyright (C) 2014 bily <bily@bily-Rev-1-0>
 *
 * Distributed under terms of the MIT license.
 */


#include<ncurses.h>     // 
#include<string.h>      // strlen
#include<unistd.h>      // usleep
#include<stdlib.h>      // malloc, free etc
#include<time.h>        // time
#include<pthread.h>     // multithreading

pthread_mutex_t lock;

typedef struct _BOX_struct{
    int startx, starty;
    int height, width;
    chtype content;
}BOX, * BOX_PTR;

typedef struct _Snake_struct{
    BOX* b;
    struct _Snake_struct* next;
}SNAKE_NODE, * SNAKE_NODE_PTR;

typedef struct{
    int ID;
    SNAKE_NODE_PTR head;
    SNAKE_NODE_PTR tail;
}SNAKE;

typedef struct{
    SNAKE* left;
    SNAKE* right;
    int left_ch;
    int right_ch;
    bool gameover;
}GAME_STATE;


void init_BOX(BOX* b, int startx, int starty, int width, int height, chtype content);
void draw_BOX(BOX* b,int color, bool flag);
void create_BOX(BOX** b, int startx, int starty);

bool check_dead(SNAKE* s, SNAKE* o, int startx_new, int starty_new);
int init_SNAKE(SNAKE** snake, int ID, int startx, int starty);
int push_SNAKE(SNAKE* snake, BOX* box);
chtype toogle_direction(chtype ch);
void print_align_center(WINDOW *win, int row, char* words);
void* threadFunc(void* arg);
int convert_key(int key);
int destroy_SNAKE(SNAKE* snake);

int main(int argc, char** argv)
{
    int ch; 
    WINDOW* border_win;

    SNAKE* left;
    SNAKE* right;
    
    // INITIALIZATION
    srand(time(NULL)); // initialize seed

    // ncurses initialization
    initscr();              // start ncurses mode
    cbreak();               // diable line buffering
                            // differs with raw(). by cbreak(), we can get Ctrl+C etc working
    keypad(stdscr, TRUE);   // enable reading of function keys like F1,F2,arrow key,etc
    noecho();               // don't display what we type
    start_color();          // we'll use color
    init_pair(1, COLOR_RED, COLOR_BLACK);
    init_pair(2, COLOR_BLUE, COLOR_BLACK);
    init_pair(3, COLOR_YELLOW, COLOR_BLACK);
    
    // draw border
    char* copyright = "BY BILY(gongbudaizhe@gmail.com)";
    mvprintw(LINES - 2, 3, "SCORE:0");
    mvprintw(LINES - 2, COLS - strlen(copyright), copyright);
   
    refresh();
    border_win = newwin(LINES - 2, COLS, 0, 0);
    box(border_win, 0, 0);
    wrefresh(border_win);

    // Welcome message
    print_align_center(stdscr, LINES / 2, "SNAKE GAME");
    print_align_center(stdscr, LINES / 2 + 1, "PRESS ANY KEY TO START");
    getch();
   
    print_align_center(stdscr, LINES / 2, "          ");
    print_align_center(stdscr, LINES / 2 + 1, "                      ");
    
    curs_set(FALSE); // we don't need blinking cursor now
    
    // GAME LOGIC
    init_SNAKE(&left, 1, 21, 10);
    init_SNAKE(&right,2, 21, 30);

    bool gameover;
    GAME_STATE state;
    state.left = left;
    state.right = right;

    state.gameover = FALSE;
    state.left_ch = KEY_RIGHT;
    state.right_ch = KEY_RIGHT;
    pthread_mutex_init(&lock, NULL);
    pthread_t pth;
    pthread_create(&pth, NULL, threadFunc, &state);
    
    while(TRUE)
    {
        ch = getch();        
        if(ch == 'q')
        {
            // exit game
            pthread_mutex_lock(&lock);
            state.gameover = TRUE;
            pthread_mutex_unlock(&lock);
            gameover = TRUE;
        }
        else if(ch == 'w' || ch == 'a' || ch == 's' || ch == 'd'){
            pthread_mutex_lock(&lock);
            state.left_ch = convert_key(ch);
            gameover = state.gameover;
            pthread_mutex_unlock(&lock);
        }else
        {
            pthread_mutex_lock(&lock);
            state.right_ch = ch;
            gameover = state.gameover;
            pthread_mutex_unlock(&lock);
        }
        if(gameover)
            break;
    }
    
    pthread_join(pth, NULL);
    destroy_SNAKE(left);
    destroy_SNAKE(right);
    endwin();
    
    return 0;
}

chtype toogle_direction(chtype ch)
{
    switch(ch)
    {
        case KEY_UP:
            return KEY_DOWN;
        case KEY_DOWN:
            return KEY_UP;
        case KEY_LEFT:
            return KEY_RIGHT;
        case KEY_RIGHT:
            return KEY_LEFT;
        default:
            return -1;
    }
}

bool check_SNAKE(SNAKE* snake, int startx, int starty)
{
    SNAKE_NODE_PTR p = snake->head->next;
    while(p)
    {
        if(p->b->startx == startx && p->b->starty == starty)
            return TRUE;    
        p = p->next;
    }
    return FALSE;
}

bool check_dead(SNAKE *s, SNAKE* other, int startx_new, int starty_new)
{
    int startx, starty;
    startx = s->tail->b->startx;
    starty = s->tail->b->starty;

    if(startx > COLS - 2 || startx < 1 || starty > LINES - 2 - 2 || starty < 1) // crash the border
        return TRUE;
    if(check_SNAKE(s, startx_new, starty_new))
        return TRUE;
    if(check_SNAKE(other, startx_new, starty_new))
        return TRUE;
    return FALSE;
}

int make_FOOD(BOX** b, SNAKE* left, SNAKE* right)
{
    *b = (BOX*) malloc(sizeof(BOX));
    int startx,starty;

    // we don't want food to be placed in the snake
    while(TRUE)
    {
        startx = 2 * (rand() % (COLS / 2 - 2)) + 1;
        starty = rand() % (LINES - 2 - 2) + 1;
        if(!check_SNAKE(left, startx, starty) && !check_SNAKE(right, startx, starty))
            break;
    }
   
    (*b)->startx = startx;
    (*b)->starty = starty;
    (*b)->width = 2;
    (*b)->height = 1;
    (*b)->content = ' ' | A_REVERSE;
    return 0;
}

int init_SNAKE(SNAKE** snake, int ID, int startx, int starty)
{
    int i;
    int width = 2;

    BOX* b;
    
    // first, we construct an empyt snake
    *snake = (SNAKE*) malloc(sizeof(SNAKE));
    (*snake)->head = (*snake)->tail = (SNAKE_NODE_PTR) malloc(sizeof(SNAKE_NODE));

    if(!(*snake)->head) return -1;
    (*snake)->head->next = NULL;
    
    (*snake)->ID = ID;

    // then, we enter some boxes
    for(i = 0; i < 5; i++)
    {
        // create box with reversed color
        create_BOX(&b, startx + width * i, starty);
        draw_BOX(b, ID, TRUE);

        // push to snake
        push_SNAKE(*snake, b);
    }
    refresh();
    return 0;
}

int destroy_SNAKE(SNAKE* snake)
{
    while(snake->head)
    {
        snake->tail = snake->head->next;
        free(snake->head->b);
        free(snake->head);
        snake->head = snake->tail;
    }
    return 0;
}

int push_SNAKE(SNAKE* snake, BOX* box)
{
    SNAKE_NODE_PTR p = (SNAKE_NODE_PTR) malloc(sizeof(SNAKE_NODE));
    if(!p) return -1; // memory allocation failed

    p->b = box;
    p->next = NULL;
    snake->tail->next = p;
    snake->tail = p;
    return 0;
}

int pop_SNAKE(SNAKE* snake, BOX** b)
{
    SNAKE_NODE_PTR p;
    if(snake->head == snake->tail)
        return -1; // empty snake

    p = snake->head->next;
    snake->head->next = p->next;
    if(snake->tail == p) 
        snake->tail = snake->head;

    *b = p->b;
    free(p);
    
    return 0;
}

void move_SNAKE(SNAKE* snake, int startx, int starty)
{
    BOX* b;
    create_BOX(&b, startx, starty);
    draw_BOX(b,snake->ID, TRUE);
    push_SNAKE(snake, b);
    pop_SNAKE(snake, &b);
    draw_BOX(b,snake->ID, FALSE);
    free(b);
}


void create_BOX(BOX ** b, int startx, int starty)
{
    *b = (BOX*) malloc(sizeof(BOX));

    (*b)->startx = startx;
    (*b)->starty = starty;
    (*b)->width = 2;
    (*b)->height = 1;
    (*b)->content = ' ' | A_REVERSE;
}

void draw_BOX(BOX *p_box, int color, bool flag)
{
    
    int i, j;
    int x,y,w,h;

    x = p_box->startx;
    y = p_box->starty;
    w = p_box->width;
    h = p_box->height;

    if(flag == TRUE){
        for(i = 0; i < w; i++)
            for(j = 0; j < h; j++)
            {
                attron(COLOR_PAIR(color));
                mvaddch(y + j, x + i, p_box->content);
                attroff(COLOR_PAIR(color));
            }
    }
    else{
        for(i = 0; i < w; i++)
            for(j = 0; j < h; j++)
                mvaddch(y + j, x + i, ' ');
    }
    refresh();
}

void print_align_center(WINDOW *win, int row, char* words)
{
     int col = (COLS - strlen(words)) / 2;
     mvwprintw(win, row, col, words);    
}

void move_pos(int* startx, int* starty, int* forbidden_direction, int ch)
{
    if(ch == (*forbidden_direction))
        ch = toogle_direction(*forbidden_direction);
    else
        *forbidden_direction = toogle_direction(ch);

    switch(ch)
    {
    case KEY_UP:
        (*starty)--;        
        break;
    case KEY_DOWN:
        (*starty)++;
        break;
    case KEY_LEFT:
        (*startx) -= 2;
        break;
    case KEY_RIGHT:
        (*startx) += 2;
        break;
    }
}
void* threadFunc(void* arg)
{
    int left_startx, left_starty;
    int right_startx, right_starty;

    bool is_dead = FALSE;
    bool left_eat_food, right_eat_food;
    bool gameover;
    int left_forbidden_direction = KEY_LEFT;
    int right_forbidden_direction = KEY_LEFT;
    int left_ch,right_ch;
    int score = 0;

    BOX * food;

    GAME_STATE* state = (GAME_STATE*) arg;
    
    make_FOOD(&food, state->left, state->right);
    draw_BOX(food, 3, TRUE);

    while(TRUE)
    {
        // add mutex for ch and gameover since these will be read or write by two processes
        pthread_mutex_lock(&lock);
        left_startx = state->left->tail->b->startx;
        left_starty = state->left->tail->b->starty;
        right_startx = state->right->tail->b->startx;
        right_starty = state->right->tail->b->starty;
        left_ch = state->left_ch;
        right_ch = state->right_ch;
        gameover = state->gameover;
        pthread_mutex_unlock(&lock);
        
        move_pos(&left_startx, &left_starty, &left_forbidden_direction, left_ch);
        move_pos(&right_startx, &right_starty, &right_forbidden_direction, right_ch);

        // if eat food then make new food
        if(left_startx == food->startx && left_starty == food->starty)
        {
            left_eat_food = TRUE;

            push_SNAKE(state->left, food);
            make_FOOD(&food, state->left, state->right);
            draw_BOX(food, 3, TRUE);
            score++;
            mvprintw(LINES - 2, 9, "%i", score);
        }
        else if(right_startx == food->startx && right_starty == food->starty)
        {
            right_eat_food = TRUE;

            push_SNAKE(state->right, food);
            make_FOOD(&food, state->left, state->right);
            draw_BOX(food,3, TRUE);
            score++;
            mvprintw(LINES - 2, 9, "%i", score);

        }else
        {
            left_eat_food = FALSE;
            right_eat_food = FALSE;
        }

        if(!left_eat_food)
        {
            is_dead = check_dead(state->left, state->right, left_startx, left_starty);
            move_SNAKE(state->left, left_startx, left_starty); 
        }
        if(!right_eat_food)
        {
            is_dead = is_dead || check_dead(state->right, state->left, right_startx, right_starty);
            move_SNAKE(state->right, right_startx, right_starty); 
        }

        refresh();
        if(is_dead || gameover){
            pthread_mutex_lock(&lock);
            state->gameover = TRUE;
            pthread_mutex_unlock(&lock);
            break;
        }
        usleep(55000);
    }
    return 0;
}

int convert_key(int key)
{
    switch(key)
    {
        case 'w':
            return KEY_UP;
        case 's':
            return KEY_DOWN;
        case 'a':
            return KEY_LEFT;
        case 'd':
            return KEY_RIGHT;
    }
    return 0;
}
